import React from "react";
import Figure from "./Figure";

/* One lesson block: the short version, a figure, a worked example, a
   question to try, or prose. Shared by the course modules and the napkin
   scenarios, so both pages render lessons the same way. */
export function Block({ b }) {
  if (b.type === "short") return <div className="lesson-short" dangerouslySetInnerHTML={{ __html: b.html }} />;
  if (b.type === "figure") return <Figure spec={b.spec} />;
  if (b.type === "example") {
    return (
      <aside className="lesson-example">
        <p className="lesson-example-h">{b.title ? `Example: ${b.title}` : "Example"}</p>
        <div dangerouslySetInnerHTML={{ __html: b.html }} />
      </aside>
    );
  }
  if (b.type === "try") {
    // The answer stays in the HTML, folded, so it reads without JavaScript.
    return (
      <details className="lesson-try">
        <summary><span className="lesson-try-h">Try it</span> {b.title}</summary>
        <div className="lesson-try-a" dangerouslySetInnerHTML={{ __html: b.html }} />
      </details>
    );
  }
  return <div className="learn-prose" dangerouslySetInnerHTML={{ __html: b.html }} />;
}

/* A lesson with a short version leads with the short version, the figure,
   the example and any question to try, and keeps the full text one tap
   away. The full text is still in the HTML, so search engines and readers
   who want depth get it. */
export function Lesson({ lesson, n }) {
  const visual = lesson.blocks.filter((b) => b.type !== "prose");
  const prose = lesson.blocks.filter((b) => b.type === "prose");
  const layered = lesson.blocks.some((b) => b.type === "short");
  const words = prose.reduce((w, b) => w + b.html.replace(/<[^>]+>/g, " ").split(/\s+/).filter(Boolean).length, 0);
  return (
    <section className="lesson" aria-labelledby={lesson.id}>
      <header className="lesson-head">
        <span className="lesson-n" aria-hidden="true">{n}</span>
        <h2 id={lesson.id} className="lesson-h">{lesson.heading}</h2>
      </header>
      {layered ? (
        <>
          {visual.map((b, i) => <Block key={i} b={b} />)}
          {prose.length > 0 && (
            <details className="lesson-more">
              <summary>Read the full lesson, with every provision it rests on ({Math.max(1, Math.round(words / 200))} min)</summary>
              {prose.map((b, i) => <Block key={i} b={b} />)}
            </details>
          )}
        </>
      ) : (
        lesson.blocks.map((b, i) => <Block key={i} b={b} />)
      )}
    </section>
  );
}
