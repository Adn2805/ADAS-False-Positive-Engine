"""Tests for vision.py — IoU and ground-truth labeling."""

from app.vision import iou, label_from_iou, batch_label_from_iou


class TestIoU:
    def test_identical_boxes(self):
        box = [0, 0, 10, 10]
        assert iou(box, box) == 1.0

    def test_no_overlap(self):
        box_a = [0, 0, 5, 5]
        box_b = [10, 10, 20, 20]
        assert iou(box_a, box_b) == 0.0

    def test_partial_overlap(self):
        """Hand-computed: boxes [0,0,10,10] and [5,5,15,15] overlap in [5,5,10,10].
        Intersection area = 5*5 = 25
        Area A = 100, Area B = 100
        Union = 100 + 100 - 25 = 175
        IoU = 25/175 ≈ 0.1429
        """
        box_a = [0, 0, 10, 10]
        box_b = [5, 5, 15, 15]
        result = iou(box_a, box_b)
        assert abs(result - 25.0 / 175.0) < 1e-6

    def test_contained_box(self):
        """Small box fully inside large box.
        Intersection = area of small box = 4
        Union = 100 + 4 - 4 = 100
        IoU = 4/100 = 0.04
        """
        big = [0, 0, 10, 10]
        small = [3, 3, 5, 5]
        result = iou(big, small)
        assert abs(result - 0.04) < 1e-6

    def test_touching_boxes(self):
        """Boxes share an edge but no area."""
        box_a = [0, 0, 5, 5]
        box_b = [5, 0, 10, 5]
        assert iou(box_a, box_b) == 0.0

    def test_zero_area_box(self):
        """A degenerate box with zero area."""
        box_a = [0, 0, 0, 0]
        box_b = [0, 0, 10, 10]
        assert iou(box_a, box_b) == 0.0


class TestLabelFromIoU:
    def test_both_none_is_tn(self):
        assert label_from_iou(None, None) == "TN"

    def test_pred_only_is_fp(self):
        assert label_from_iou([0, 0, 5, 5], None) == "FP"

    def test_true_only_is_fn(self):
        assert label_from_iou(None, [0, 0, 5, 5]) == "FN"

    def test_good_overlap_is_tp(self):
        box = [0, 0, 10, 10]
        assert label_from_iou(box, box) == "TP"

    def test_bad_overlap_is_fp(self):
        pred = [0, 0, 10, 10]
        true = [50, 50, 60, 60]
        assert label_from_iou(pred, true) == "FP"

    def test_custom_iou_threshold(self):
        # Partial overlap ≈ 0.143 — should be FP at default 0.5, but TP at 0.1
        pred = [0, 0, 10, 10]
        true = [5, 5, 15, 15]
        assert label_from_iou(pred, true, iou_threshold=0.5) == "FP"
        assert label_from_iou(pred, true, iou_threshold=0.1) == "TP"


class TestBatchLabel:
    def test_batch(self):
        preds = [[0, 0, 10, 10], None, [50, 50, 60, 60], None]
        trues = [[0, 0, 10, 10], [0, 0, 5, 5], None, None]
        labels = batch_label_from_iou(preds, trues)
        assert labels == ["TP", "FN", "FP", "TN"]
