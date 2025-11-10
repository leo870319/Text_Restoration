## 4. Footnote Compilation

Footnotes can be categorized by their forms of labeling as follows:

- **author_notes**
  - Notes start with `1). `, `2). `, etc.
- **editor_notes**
  - Notes start with `1. `, `2. `, etc.
- **critical_apparatus**
  - Notes start with `a. `, `b. `, `i. `, `p. ` etc.
  - Notes start with `s - s. ` `t - t. ` etc.

Retain footnotes added by authors and editors; remove critical apparatus.

## 6. In-text Marker Handling

In-text markers can be categorized by their forms of notation as follows:

- `1)`, `2)`, `3)`: Markers referencing author_notes.
- `1`, `2`, `3`: Markers referencing the editor_notes.
- `a`, `b`, `c`: Markers referencing critical_apparatus.
- `a ... a`, `b ... b`: Range-Markers referencing th critical_apparatus, indicating the start and end of a textual intervention.
- `A1`, `A2`, `A3`: Page numbering of the manuscripts.

We can locate In-text Markers that refer to footnotes by using the labels of footnotes already identified at the bottom of the page (e.g., `1)`, `a`, `4`).

- **Markers for Editor's and Author's footnotes** must be enclosed in square brackets.
  - Author's notes: `4)` becomes `[4)]`
  - Editor's notes: `17` becomes `[17]`

- **Remove other in-text markers from text:**
  - Markers referencing critical_apparatus.
  - Page numbering of the manuscripts (e.g., A2, B5)
  - Line numbers (which are occasionally captured in OCR by accident)

- **Split Compound Markers**: When multiple tags appear simultaneously (e.g. `4)o`), distinguish by their categories and discard the unwanted ones.
  - **Example**: `...warum ? 4)o Ob...` **must** be restored as `...warum?[4)] Ob...`. (Discard `o` as it belongs to critical_apparatus)
