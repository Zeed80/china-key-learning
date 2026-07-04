import { describe, expect, it } from "vitest";

import { autoMark } from "./OverviewPage";

describe("autoMark", () => {
  it("marks visual differences in confusable descriptions", () => {
    expect(autoMark("левая форма шире, правая форма уже")).toContain("__MARK__левая форма");
    expect(autoMark("левая форма шире, правая форма уже")).toContain("__MARK__шире");
    expect(autoMark("левая форма шире, правая форма уже")).toContain("__MARK__уже");
  });
});
