import type { Radical, RadicalListItem } from "../api/types";

type Props = {
  radical: Radical | RadicalListItem;
  size?: "sm" | "md" | "lg";
};

export function RadicalGlyph({ radical, size = "md" }: Props) {
  const svg = "assets" in radical ? radical.assets[0]?.payload : radical.asset_svg;
  return (
    <div className={`glyph glyph-${size}`} aria-label={`Ключ ${radical.character}`}>
      {svg ? <span dangerouslySetInnerHTML={{ __html: svg }} /> : <span className="glyph-fallback">{radical.character}</span>}
    </div>
  );
}
