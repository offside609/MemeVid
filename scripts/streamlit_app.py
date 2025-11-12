"""Streamlit UI for human-in-the-loop caption selection and rendering."""

import asyncio
from pathlib import Path

import httpx
import streamlit as st

API_BASE = "http://localhost:8000"  # FastAPI server URL


async def start_workflow(media_path: str) -> dict:
    """Trigger the initial workflow run up to the human review interrupt."""
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{API_BASE}/jokestruc/generate",
            json={"media_path": media_path},
        )
        resp.raise_for_status()
        return resp.json()


async def resume_workflow(thread_id: str, user_selected_caption: str) -> dict:
    """Resume the paused workflow with the human-selected caption."""
    payload = {"thread_id": thread_id, "user_selected_caption": user_selected_caption}
    st.write("Posting resume payload:", payload)
    async with httpx.AsyncClient(timeout=180) as client:
        resp = await client.post(f"{API_BASE}/jokestruc/resume", json=payload)
        st.write("Resume response status:", resp.status_code)
        st.write("Resume response body:", resp.text)
        resp.raise_for_status()
        return resp.json()


def main() -> None:
    """Run the Streamlit app."""
    st.set_page_config(page_title="MemeVid Human Review", layout="wide")
    st.title("MemeVid Human-in-the-Loop")

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
        st.session_state.candidates = []
        st.session_state.video_insight = None
        st.session_state.scene_map = None
        st.session_state.logs = []
        st.session_state.output = None

    uploaded_file = st.file_uploader("Upload video", type=["mp4", "mov", "mkv"])
    if uploaded_file and st.button("Run Workflow"):
        # Persist temp file
        tmp_path = Path("tmp_upload.mp4")
        tmp_path.write_bytes(uploaded_file.read())

        with st.spinner("Running analysis..."):
            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(
                    start_workflow(str(tmp_path.resolve()))
                )
            finally:
                loop.close()

        st.session_state.thread_id = result["thread_id"]
        if result.get("status") == "awaiting_review":
            payload = result.get("payload", {})
            raw_candidates = payload.get("candidates", [])
            if isinstance(raw_candidates, str):
                candidates = [
                    line.strip() for line in raw_candidates.splitlines() if line.strip()
                ]
            else:
                candidates = raw_candidates

            st.session_state.candidates = candidates
        elif result.get("status") == "completed":
            state = result.get("state", {})
            st.session_state.video_insight = state.get("video_insights")
            st.session_state.logs = state.get("logs", [])

    if st.session_state.thread_id:
        st.subheader("Video Insight")
        st.json(st.session_state.video_insight or {})

        st.subheader("Candidate Captions")
        for i, caption in enumerate(st.session_state.candidates, start=1):
            st.markdown(f"{i}. {caption}")

        # st.text_area("Scene map", st.session_state.scene_map or "", height=150)

        st.subheader("Select Caption")
        chosen_caption = st.selectbox(
            "Pick a caption",
            options=st.session_state.candidates,
            index=0 if st.session_state.candidates else None,
        )
        # custom_caption = st.text_input(
        #     "Or type your own",
        #     value=chosen_caption if chosen_caption else "",
        # )
        # reason = st.text_input("Why this caption? (optional)")

        if st.button("Render Final Meme"):
            final_caption = chosen_caption
            with st.spinner("Rendering..."):
                loop = asyncio.new_event_loop()
                try:
                    result = loop.run_until_complete(
                        resume_workflow(
                            st.session_state.thread_id,
                            final_caption,
                            # reason or "Selected via Streamlit UI",
                        )
                    )
                finally:
                    loop.close()

            st.session_state.output = result["state"]
            st.success("Rendering complete!")

    if st.session_state.output:
        output_state = st.session_state.output
        st.subheader("Final Meme")
        output_path = output_state.get("output_target")
        if output_path and Path(output_path).exists():
            st.video(str(Path(output_path).resolve()))
        else:
            st.write("Output video path:", output_path)

        st.subheader("Timing Plan")
        st.json(output_state.get("timing_plan"))

        st.subheader("Logs")
        st.json(output_state.get("logs"))


if __name__ == "__main__":
    main()
