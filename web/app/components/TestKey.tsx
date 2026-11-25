"use client";

import { useState } from "react";
import type { Prompt } from "../lib/api";
import { TONE_LABEL, TONE_TEXT, toneOfRarity, type Tone } from "../lib/game";
import { Label, Panel } from "./ui";

const ORDER: Tone[] = ["golden", "deepcut", "rare", "uncommon", "common"];

/**
 * Test dive only: the current prompt's answer key. Click an answer to dive with it (the real game path,
 * so the verdict, fish, depth and results all play out); type a decoy or a typo to see rejections.
 */
export function TestKey({ prompt, onPick }: { prompt?: Prompt; onPick?: (answer: string, force?: boolean) => void }) {
  const [open, setOpen] = useState(true);
  const play = prompt?.play;
  const tiers = ORDER.map((tone) => ({
    tone,
    names: (play?.answers ?? []).filter((a) => (a.golden ? "golden" : toneOfRarity(a.rarity)) === tone).map((a) => a.names),
  })).filter((t) => t.names.length);

  return (
    <Panel className="fixed bottom-3 right-3 z-40 w-[min(22rem,calc(100vw-1.5rem))] text-sm">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full cursor-pointer items-center justify-between px-4 py-2 text-left"
        aria-expanded={open}
      >
        <Label className="text-gold">Test dive · answer key</Label>
        <span className="font-pixel text-mist">{open ? "–" : "+"}</span>
      </button>
      {open && (
        <div className="max-h-[55vh] overflow-y-auto border-t-2 border-line px-4 pb-4 pt-3">
          {!prompt || !onPick ? (
            <p className="text-xs leading-relaxed text-mist">
              Every prompt in the McGill bank, scored like a fresh day. Nothing is saved or sent. Refresh to start over.
            </p>
          ) : (
            <>
              {tiers.map(({ tone, names }) => (
                <div key={tone} className="mb-3">
                  <Label className={TONE_TEXT[tone]}>{TONE_LABEL[tone]}</Label>
                  <ul className="mt-1.5 flex flex-wrap gap-1.5">
                    {names.map((n) => (
                      <li key={n[0]}>
                        <button
                          onClick={() => onPick(n[0])}
                          title={n.length > 1 ? `Also accepts: ${n.slice(1).join(", ")}` : undefined}
                          className="cursor-pointer border border-line bg-abyss/60 px-2 py-0.5 text-xs text-ink hover:border-mist"
                        >
                          {n[0]}
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
              {!!play?.decoys.length && (
                <div className="mb-3">
                  <Label className="text-coral">Decoys · type one to see a rejection</Label>
                  <p className="mt-1.5 text-xs leading-relaxed text-slate">{play.decoys.join(" · ")}</p>
                </div>
              )}
              <button
                onClick={() => onPick("", true)}
                className="mt-1 cursor-pointer text-xs uppercase tracking-[0.2em] text-foam underline underline-offset-4 hover:text-ink"
              >
                Run out of air
              </button>
            </>
          )}
        </div>
      )}
    </Panel>
  );
}
