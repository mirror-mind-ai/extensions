/**
 * Maestro Visibility Spike
 *
 * Deterministically prepends Maestro checkpoint visuals to assistant checkpoint
 * messages in Pi, instead of relying on the model to remember to call the
 * Maestro CLI. This is intentionally narrow and experimental.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { StringEnum } from "@earendil-works/pi-ai";
import { Text } from "@earendil-works/pi-tui";
import { Type } from "typebox";

const MAX_SCAN_CHARS = 20_000;

type Checkpoint = "plan" | "implement" | "validate" | "review" | "coherence" | "commit";

type MaestroCheckpointDetails = {
	checkpoint?: Checkpoint;
	journey?: string;
	story?: string;
	visual?: string;
	skipped?: boolean;
	reason?: string;
};

function textFromContent(content: unknown): string {
	if (typeof content === "string") return content;
	if (!Array.isArray(content)) return "";
	return content
		.filter((block): block is { type: string; text: string } => {
			return !!block && typeof block === "object" && (block as any).type === "text" && typeof (block as any).text === "string";
		})
		.map((block) => block.text)
		.join("\n");
}

function detectJourneyFromText(text: string): string | null {
	const patterns = [
		/Builder Mode (?:active|ativo) (?:for|para)\s+([a-z0-9][a-z0-9_-]*)/i,
		/\/mm-build\s+([a-z0-9][a-z0-9_-]*)/i,
		/--journey\s+([a-z0-9][a-z0-9_-]*)/i,
		/Journey:\s*([a-z0-9][a-z0-9_-]*)/i,
		/jornada\s+([a-z0-9][a-z0-9_-]*)/i,
	];
	for (const pattern of patterns) {
		const match = text.match(pattern);
		if (match?.[1] && !["slug", "journey", "project"].includes(match[1].toLowerCase())) return match[1];
	}

	// Sandbox-specific convenience for the visibility spike. The project folder is
	// maestro-sandbox-pet-store while the Mirror journey is sandbox-pet-store.
	if (/maestro-sandbox-pet-store|sandbox-pet-store/i.test(text)) return "sandbox-pet-store";
	return null;
}

function recentConversationText(ctx: any): string {
	try {
		const branch = ctx.sessionManager.getBranch?.() ?? [];
		const tail = branch.slice(-20).map((entry: any) => {
			if (entry?.type !== "message") return "";
			return textFromContent(entry.message?.content);
		});
		return tail.join("\n").slice(-MAX_SCAN_CHARS);
	} catch {
		return "";
	}
}

function normalizeCoherenceItem(value: string): string {
	const text = value.trim();
	if (!text) return "Surface:unknown";
	if (text.includes(":")) return text;

	const match = text.match(/^(Roadmap|Decisions|Worklog|README|Tests?|Docs?|Release|Version)(?:\s*[-—:]\s*(.*))?$/i);
	if (match?.[1]) {
		const surface = match[1];
		const detail = match[2]?.trim();
		return detail ? `${surface}:checked:${detail}` : `${surface}:checked`;
	}

	const dash = text.match(/^([^—-]+)\s*[-—]\s*(.+)$/);
	if (dash?.[1] && dash?.[2]) return `${dash[1].trim()}:checked:${dash[2].trim()}`;

	return `${text}:checked`;
}

function normalizeRoadmapItem(value: string): string {
	const text = value.trim();
	if (!text) return "";
	if (text.includes(":")) return text;

	const match = text.match(/^(cv|epic|story)\s+([^—-]+?)\s*[-—]\s*([^—-]+?)(?:\s*[-—]\s*(done|active|next|planned|radar|blocked))?$/i);
	if (match?.[1] && match?.[2] && match?.[3]) {
		return `${match[1].toLowerCase()}:${match[2].trim()}:${match[3].trim()}:${(match[4] ?? "active").toLowerCase()}`;
	}

	return text;
}

function hasCompleteWorkMap(params: any): boolean {
	return [params.cvCode, params.cvTitle, params.epicCode, params.epicTitle, params.story].every(
		(value) => typeof value === "string" && value.trim().length > 0,
	);
}

export default function (pi: ExtensionAPI) {
	// Until Maestro is wired to Mirror journey context directly, keep a local
	// journey hint so the structured tool can supply a default --journey value.
	let activeJourney: string | null = "sandbox-pet-store";
	let maestroEnabled = true;

	pi.registerTool({
		name: "maestro_checkpoint",
		label: "Maestro Checkpoint",
		description: "Render a structured Ariad/Maestro checkpoint visual from explicit checkpoint data.",
		promptSnippet: "Render a Maestro checkpoint visual from structured journey, story, checkpoint, validation, and coherence data",
		promptGuidelines: [
			"Use maestro_checkpoint at Ariad checkpoints instead of hand-drawing Maestro visuals or running the Maestro CLI through bash.",
			"Call maestro_checkpoint before checkpoint prose when work reaches plan, validate, coherence, or story-close boundaries.",
			"Use checkpoint=commit for story-close even when no git commit will be created; explain the no-git or no-commit reason in statusSentence.",
		],
		parameters: Type.Object({
			journey: Type.Optional(Type.String({ description: "Mirror journey slug, for example sandbox-pet-store" })),
			checkpoint: StringEnum(["plan", "implement", "validate", "review", "coherence", "commit"] as const),
			story: Type.Optional(Type.String({ description: "Story code and title, for example CV1.E1.S2 Update quantity" })),
			cvCode: Type.Optional(Type.String()),
			cvTitle: Type.Optional(Type.String()),
			epicCode: Type.Optional(Type.String()),
			epicTitle: Type.Optional(Type.String()),
			statusSentence: Type.Optional(Type.String()),
			recommendedNext: Type.Optional(Type.String()),
			automated: Type.Optional(Type.String({ description: "Automated evidence detail, for example npm test passed; npm run build passed" })),
			automatedState: Type.Optional(StringEnum(["passed", "attention", "blocked", "not_run", "unknown"] as const)),
			manual: Type.Optional(Type.String({ description: "Manual validation detail" })),
			manualState: Type.Optional(StringEnum(["passed", "attention", "blocked", "not_run", "unknown"] as const)),
			blocker: Type.Optional(Type.String()),
			risk: Type.Optional(Type.String({ description: "Risk posture detail" })),
			riskState: Type.Optional(StringEnum(["passed", "attention", "blocked", "not_run", "unknown"] as const)),
			coherence: Type.Optional(Type.Array(Type.String({ description: "Coherence item as Surface:state[:detail], e.g. Roadmap:checked:story marked done" }))),
			roadmap: Type.Optional(Type.Array(Type.String({ description: "Roadmap item as level:code:title:status[:done/total], e.g. story:CV1.E2.S2:Continue shopping:done" }))),
		}),
		renderShell: "self",
		async execute(_toolCallId, params: any, signal) {
			if (!hasCompleteWorkMap(params)) {
				return {
					content: [{ type: "text", text: "" }],
					details: { skipped: true, reason: "incomplete_work_map" } satisfies MaestroCheckpointDetails,
				};
			}

			const args = [
				"run",
				"python",
				"-m",
				"memory",
				"ext",
				"maestro",
				"checkpoint",
				"--checkpoint",
				params.checkpoint,
			];

			const add = (flag: string, value?: string) => {
				if (typeof value === "string" && value.trim()) args.push(flag, value.trim());
			};
			add("--journey", params.journey ?? activeJourney ?? undefined);
			add("--story", params.story);
			add("--cv-code", params.cvCode);
			add("--cv-title", params.cvTitle);
			add("--epic-code", params.epicCode);
			add("--epic-title", params.epicTitle);
			add("--status-sentence", params.statusSentence);
			add("--recommended-next", params.recommendedNext);

			const validationCheckpoint = params.checkpoint === "validate" || params.checkpoint === "commit";
			if (validationCheckpoint && params.automated) add("--automated", `Automated checks:${params.automatedState ?? "passed"}:${params.automated}`);
			if (validationCheckpoint && params.manual) add("--manual", `Manual validation:${params.manualState ?? "passed"}:${params.manual}`);
			if (validationCheckpoint) add("--blocker", params.blocker);
			if (validationCheckpoint && params.risk) add("--risk", `Risk posture:${params.riskState ?? "unknown"}:${params.risk}`);
			const coherenceCheckpoint = params.checkpoint === "coherence" || params.checkpoint === "commit";
			if (coherenceCheckpoint) {
				for (const item of params.coherence ?? []) add("--coherence", normalizeCoherenceItem(item));
			}
			if (params.checkpoint === "commit") {
				for (const item of params.roadmap ?? []) {
					const normalized = normalizeRoadmapItem(item);
					if (normalized) add("--roadmap", normalized);
				}
			}

			const result = await pi.exec("uv", args, { signal, timeout: 15_000 });
			const stdout = (result.stdout ?? "").trim();
			const stderr = (result.stderr ?? "").trim();
			if (result.code !== 0 || !stdout) {
				throw new Error(stderr || `Maestro checkpoint failed with code ${result.code}`);
			}
			return {
				content: [{ type: "text", text: stdout }],
				details: { checkpoint: params.checkpoint, journey: params.journey ?? activeJourney, story: params.story, visual: stdout } satisfies MaestroCheckpointDetails,
			};
		},

		renderCall(args, theme) {
			if (!hasCompleteWorkMap(args)) return new Text("", 0, 0);
			const rawCheckpoint = typeof args.checkpoint === "string" ? args.checkpoint : "checkpoint";
			const checkpoint = rawCheckpoint.charAt(0).toUpperCase() + rawCheckpoint.slice(1);
			const story = typeof args.story === "string" ? args.story : "";
			const suffix = story ? theme.fg("dim", ` · ${story}`) : "";
			return new Text(theme.fg("toolTitle", theme.bold(`Maestro checkpoint: ${checkpoint}`)) + suffix, 0, 0);
		},

		renderResult(result, _options, theme) {
			const details = result.details as MaestroCheckpointDetails | undefined;
			if (details?.skipped) return new Text("", 0, 0);
			const visual = details?.visual ?? result.content.find((item: any) => item?.type === "text")?.text ?? "";
			const lines = visual
				.split("\n")
				.filter((line, index) => !(index === 0 && line === "Maestro checkpoint"))
				.map((line) => {
					if (line.startsWith("Ariad:")) return theme.fg("accent", line);
					if (["Validation Panel", "Coherence Matrix", "Roadmap Snapshot", "Recommended next"].includes(line)) {
						return theme.fg("toolTitle", theme.bold(line));
					}
					if (line.startsWith("✅") || line.startsWith("✓")) return theme.fg("success", line);
					if (line.startsWith("⚠")) return theme.fg("warning", line);
					if (line.startsWith("⛔") || line.startsWith("✕")) return theme.fg("error", line);
					if (line.startsWith("?") || line.startsWith("○") || line.startsWith("-")) return theme.fg("muted", line);
					return theme.fg("text", line);
				})
				.join("\n");
			return new Text(lines, 0, 0);
		},
	});

	function renderStatus(): string {
		return maestroEnabled ? "♪ Maestro · on" : "♪ Maestro · off";
	}

	function refreshStatus(ctx?: any): void {
		if (ctx?.hasUI) ctx.ui.setStatus("maestro", renderStatus());
	}

	function setActiveJourney(journey: string | null, ctx?: any): void {
		if (!journey) return;
		if (["slug", "journey", "project"].includes(journey.toLowerCase())) return;
		activeJourney = journey;
		refreshStatus(ctx);
	}

	pi.registerCommand("maestro", {
		description: "Control Maestro checkpoint protocol: /maestro on|off|status [journey]",
		handler: async (args, ctx) => {
			const [actionRaw, journeyRaw] = args.trim().split(/\s+/, 2);
			const action = (actionRaw || "status").toLowerCase();

			if (action === "on" || action === "enable") {
				maestroEnabled = true;
				setActiveJourney(journeyRaw ?? activeJourney, ctx);
				refreshStatus(ctx);
				ctx.ui.notify(`Maestro checkpoint protocol on${activeJourney ? ` · ${activeJourney}` : ""}`, "info");
				return;
			}

			if (action === "off" || action === "disable") {
				maestroEnabled = false;
				refreshStatus(ctx);
				ctx.ui.notify("Maestro checkpoint protocol off", "info");
				return;
			}

			if (action === "status") {
				if (journeyRaw) setActiveJourney(journeyRaw, ctx);
				refreshStatus(ctx);
				ctx.ui.notify(`Maestro checkpoint protocol ${maestroEnabled ? "on" : "off"}${activeJourney ? ` · ${activeJourney}` : ""}`, "info");
				return;
			}

			// Convenience: /maestro sandbox-pet-store sets the journey and turns on.
			maestroEnabled = true;
			setActiveJourney(actionRaw, ctx);
			refreshStatus(ctx);
			ctx.ui.notify(`Maestro checkpoint protocol on${activeJourney ? ` · ${activeJourney}` : ""}`, "info");
		},
	});

	pi.registerCommand("maestro-visibility", {
		description: "Set Maestro checkpoint journey, e.g. /maestro-visibility sandbox-pet-store",
		handler: async (args, ctx) => {
			const journey = args.trim() || "sandbox-pet-store";
			setActiveJourney(journey, ctx);
			ctx.ui.notify(`Maestro checkpoint journey set: ${journey}`, "info");
		},
	});

	pi.on("session_start", async (_event, ctx) => {
		setActiveJourney(detectJourneyFromText(recentConversationText(ctx)) ?? activeJourney, ctx);
		refreshStatus(ctx);
	});

	pi.on("before_agent_start", async (event) => {
		if (!maestroEnabled || !activeJourney) return;
		return {
			systemPrompt:
				event.systemPrompt +
				`\n\nMaestro structured checkpoint protocol is active for journey ${activeJourney}. At Ariad checkpoint boundaries, call the maestro_checkpoint tool before prose. Do not hand-draw Maestro visuals in Markdown. Use checkpoint=plan for planning checkpoints, implement for implementation-start orientation, validate for validation checkpoints, review for review/documentation handoff, coherence for coherence checks, and commit for story-close even when no git commit will be created. If no git commit is created, state that reason in statusSentence instead of skipping the story-close checkpoint. Include roadmap items on commit/story-close when known so Roadmap Snapshot can render.`,
		};
	});

	pi.on("input", async (event, ctx) => {
		setActiveJourney(detectJourneyFromText((event as any).text ?? ""), ctx);
		return { action: "continue" };
	});

}
