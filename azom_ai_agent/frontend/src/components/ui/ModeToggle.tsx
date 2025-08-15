import { useMode } from "@/context/ModeContext";

export function ModeToggle() {
  const { mode, toggle } = useMode();
  return (
    <button
      type="button"
      onClick={toggle}
      className="inline-flex items-center gap-2 text-xs px-2 py-1 rounded-md border hover:bg-accent"
      aria-pressed={mode === "light"}
      title="Toggle Light/Full mode"
    >
      <span className="font-medium">Mode:</span>
      <span className="uppercase">{mode}</span>
    </button>
  );
}
