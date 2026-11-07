
def build_xfade_filter(
    durations: list[float],
    transition_duration: float = 0.45
):
    """
    Builds an FFmpeg xfade filter graph.

    Returns:
        filter_complex: FFmpeg filter graph
        total_duration: Final video duration
    """

    if len(durations) < 2:
        raise ValueError("At least two clips are required")

    if any(duration <= transition_duration for duration in durations):
        raise ValueError(
            "Each clip must be longer than the transition duration"
        )

    filters = []

    for index in range(len(durations)):

        filters.append(
            f"[{index}:v]"
            f"settb=AVTB,"
            f"setpts=PTS-STARTPTS,"
            f"fps=30,"
            f"format=yuv420p"
            f"[v{index}]"
        )

    current_label = "v0"
    elapsed = durations[0]

    for index in range(1, len(durations)):

        offset = elapsed - transition_duration

        next_label = f"vx{index}"

        filters.append(
            f"[{current_label}][v{index}]"
            f"xfade=transition=fade:"
            f"duration={transition_duration}:"
            f"offset={offset:.3f}"
            f"[{next_label}]"
        )

        current_label = next_label
        elapsed += durations[index] - transition_duration

    filters.append(
        f"[{current_label}]format=yuv420p[vout]"
    )

    total_duration = (
        sum(durations)
        - transition_duration * (len(durations) - 1)
    )

    return ";".join(filters), total_duration
