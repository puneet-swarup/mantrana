from src.mantrana.log import Log


def test_append_and_render() -> None:
    log = Log()
    log.append("HUMAN", "hello")
    log.append("MODERATOR", "hi")
    assert "[HUMAN]: hello" in log.render()
    assert "[MODERATOR]: hi" in log.render()


def test_pinned_survives_trim() -> None:
    log = Log(trim_after=2)
    log.pin("PROBLEM", "the goal")
    for i in range(10):
        log.append("X", f"msg{i}")
    rendered = log.render_trimmed()
    assert "the goal" in rendered
    assert "msg9" in rendered
    assert "msg0" not in rendered


def test_turn_count_excludes_pinned() -> None:
    log = Log()
    log.pin("PROBLEM", "goal")
    log.append("X", "a")
    log.append("Y", "b")
    assert log.turn_count() == 2


def test_pinned_kept_in_original_position() -> None:
    log = Log(trim_after=5)
    log.append("A", "first")
    log.pin("PROBLEM", "pinned")
    log.append("B", "second")
    rendered = log.render_trimmed()
    assert rendered.index("first") < rendered.index("pinned")
    assert rendered.index("pinned") < rendered.index("second")