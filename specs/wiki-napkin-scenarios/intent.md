# Intent: six napkin scenarios on dpdpa.wiki

**Status:** approved (mockup and evals, 2026-11-26)
**Owner:** Dilip Sahu
**Date:** 2026-11-26

## Problem

The course explains the Act provision by provision. Readers who are not lawyers still
ask simple, concrete questions: who is responsible, how big a penalty can get, where
their data may go, when the duties start, how to get data erased, and why a business may
use one piece of data and not another. Dan Roam's Back of the Napkin method answers each
kind of question with one kind of picture. Dilip approved a mockup that applies it to one
customer and one tiffin service.

## Goals

### G1 — Any reader can follow six everyday DPDPA scenarios from pictures
One page, one story, six questions, each answered with one figure, plain words an
8th-grader can read, and a question to try.

### G2 — Every statement on the page is as checkable as the course
Quotes match the gazette text word for word, every citation is within the page's list,
and amounts and dates come only from the Schedule and the Rules.

## Assumptions

### A1 — The module format and citation gate can carry the page unchanged
- validate_by: the page builds from Markdown through module-build.js and passes check-citations.mjs

### A2 — Two new figure types (map, plot) are enough for "where" and "why"
- validate_by: the figures render without JavaScript and pass a first-time reader's check

### A3 — One made-up customer and an unnamed business keep real companies off the page
- validate_by: the page names no business; Asha and the tiffin service are said to be made up

## Out of scope

Translations, new provisions, the course's six modules, and any change to the law file.
