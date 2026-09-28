import { useEffect } from "react";

/**
 * Sets document.title after client-side navigation and restores it on unmount.
 * The prerender already writes the title into the HTML, so this only matters
 * once the reader moves between pages without a reload.
 */
export function usePageTitle(title) {
  useEffect(() => {
    if (!title) return undefined;
    const prev = document.title;
    document.title = title;
    return () => { document.title = prev; };
  }, [title]);
}
