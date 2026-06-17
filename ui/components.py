"""
Reusable Streamlit render components — one per agent response type.
Each function knows how to display its data type beautifully.
"""
import streamlit as st
from typing import Any

# Badge config: agent_type → (emoji, label, css_class)
_BADGES = {
    "weather":    ("🌤️", "WEATHER",  "badge-weather"),
    "forex":      ("💱", "FOREX",    "badge-forex"),
    "music":      ("🎵", "MUSIC",    "badge-music"),
    "music_text": ("🎵", "MUSIC",    "badge-music"),
    "news":       ("📰", "NEWS",     "badge-news"),
    "general":    ("🤖", "AI·GROK", "badge-general"),
    "error":      ("⚠️", "ERROR",    "badge-error"),
}


def render_agent_badge(response_type: str) -> None:
    icon, label, css = _BADGES.get(response_type, ("🤖", "AI", "badge-general"))
    st.markdown(
        f'<span class="agent-badge {css}">{icon}&nbsp;{label}</span>',
        unsafe_allow_html=True,
    )


def render_music_player(music_data: dict) -> None:
    """Render YouTube embed + result list."""
    embed_url = music_data.get("embed_url", "")
    title     = music_data.get("title", "Now Playing")
    channel   = music_data.get("channel", "")
    watch_url = music_data.get("watch_url", "")

    if embed_url:
        st.markdown(
            f'<div class="music-card">'
            f'<iframe src="{embed_url}" height="200" '
            f'allow="accelerometer; autoplay; clipboard-write; '
            f'encrypted-media; gyroscope; picture-in-picture" allowfullscreen>'
            f'</iframe></div>',
            unsafe_allow_html=True,
        )
        st.caption(f"🎵 **{title}** · {channel}  [▶ Open on YouTube]({watch_url})")

    # Additional results
    others = music_data.get("all_results", [])
    if len(others) > 1:
        with st.expander("🎶 More results"):
            for i, v in enumerate(others[1:6], 2):
                c1, c2 = st.columns([5, 1])
                c1.markdown(f"**{i}.** {v.get('title','')}")
                c2.markdown(f"[▶]({v.get('watch_url','#')})")


def render_response(agent_response: dict[str, Any], final_answer: str) -> None:
    """
    Master dispatcher — reads agent_response['type'] and renders the
    appropriate UI component.
    """
    rtype = (agent_response or {}).get("type", "general")
    render_agent_badge(rtype)

    if rtype == "music":
        st.write(final_answer)
        render_music_player(agent_response.get("data", {}))
    else:
        st.markdown(final_answer)


def render_routing_sidebar(metadata: dict) -> None:
    """Show the last routing decision in the sidebar."""
    route = metadata.get("route", "")
    conf  = metadata.get("confidence", 0.0)
    if route:
        st.sidebar.divider()
        st.sidebar.caption("🔀 **LAST ROUTE**")
        c1, c2 = st.sidebar.columns(2)
        c1.metric("Agent",      route.upper())
        c2.metric("Confidence", f"{conf:.0%}")
