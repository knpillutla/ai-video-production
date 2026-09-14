"""Unit Tests for Studio Right Preview Panel and Fullscreen Video Controls."""

from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app
from src.api.ui_composer import render_studio_html


def test_ui_studio_right_preview_panel_elements():
    """Verify studio UI contains right preview panel, video player, and fullscreen buttons."""
    content = render_studio_html()
    js_content = "\n".join(f.read_text(encoding="utf-8") for f in Path("src/static/js").glob("*.js"))
    full_content = content + "\n" + js_content

    # Right panel structure and controls
    assert 'id="studio-preview-panel"' in content
    assert 'id="btn-expand-right-panel"' in content
    assert 'id="btn-close-right-panel"' in content
    assert 'id="btn-toggle-panel"' in content

    # Master video player and video fullscreen controls
    assert 'id="studio-panel-video"' in content
    assert 'id="btn-panel-play-video"' in content
    assert 'id="btn-expand-video-fullscreen"' in content
    assert 'id="studio-panel-processing-overlay"' in content

    # Metadata and timestamp fields in the right panel
    assert 'id="panel-video-title"' in content
    assert 'id="panel-video-concept"' in content
    assert 'id="panel-video-status-badge"' in content
    assert 'id="panel-meta-jobid"' in content
    assert 'id="panel-meta-videotype"' in content
    assert 'id="panel-meta-format-style"' in content
    assert 'id="panel-meta-tier-cost"' in content
    assert 'id="panel-ts-created"' in content
    assert 'id="panel-ts-started"' in content
    assert 'id="panel-ts-completed"' in content
    assert 'id="panel-ts-published"' in content
    assert 'id="panel-btn-artifacts"' in content
    assert 'id="panel-btn-youtube"' in content

    # JavaScript controller functions
    assert "selectLedgerVideo" in full_content
    assert "toggleRightPanelFullscreen" in full_content
    assert "expandVideoFullscreen" in full_content
    assert "togglePanelVideoPlay" in full_content
    assert "onLedgerRowClick" in full_content
    assert "toggleRightPanelVisibility" in full_content


@pytest.mark.asyncio
async def test_preview_panel_static_assets_serving():
    """Verify preview_panel.js and preview_master.mp4 are served with HTTP 200."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        js_resp = await ac.get("/static/js/preview_panel.js")
        assert js_resp.status_code == 200
        assert "selectLedgerVideo" in js_resp.text
        assert "toggleRightPanelFullscreen" in js_resp.text
        assert "expandVideoFullscreen" in js_resp.text

        video_resp = await ac.get("/static/videos/preview_master.mp4")
        assert video_resp.status_code == 200
        assert "video/mp4" in video_resp.headers.get("content-type", "")


def test_ui_creation_modes_theme_idea_script():
    """Verify Theme, Idea, Script mode pills are rendered with Theme active by default."""
    content = render_studio_html()
    js_content = "\n".join(f.read_text(encoding="utf-8") for f in Path("src/static/js").glob("*.js"))
    full_content = content + "\n" + js_content

    # Mode buttons in hero card
    assert 'id="mode-pill-theme"' in content
    assert 'id="mode-pill-idea"' in content
    assert 'id="mode-pill-script"' in content

    # Default placeholder and hint
    assert "explore niagara falls" in content
    assert 'id="creation-mode-hint"' in content

    # JavaScript controller
    assert "setCreationMode" in full_content
    assert 'currentCreationMode = "theme"' in full_content
    assert "usePresetPrompt" in full_content
    assert "MODE_STARTERS" in full_content
    assert "flashPromptInput" in full_content


def test_ui_separated_creation_and_ledger_screens():
    """Verify video creation panel and history ledger list are separated on dedicated tabs."""
    from pathlib import Path
    studio_html = Path("src/templates/components/tabs/studio.html").read_text(encoding="utf-8")
    ledger_html = Path("src/templates/components/tabs/ledger.html").read_text(encoding="utf-8")
    sidebar_html = Path("src/templates/components/layout/sidebar.html").read_text(encoding="utf-8")

    # Creation screen: has prompt, tier pills, generate button, but NO history table rows
    assert 'id="youtube-prompt-input"' in studio_html
    assert 'id="btn-guided-generate"' in studio_html
    assert 'id="studio-video-history-rows"' not in studio_html

    # Ledger screen: has history table rows and includes preview panel, but NO prompt input
    assert 'id="studio-video-history-rows"' in ledger_html
    assert 'studio_preview_panel.html' in ledger_html
    assert 'id="youtube-prompt-input"' not in ledger_html

    # Sidebar: has separate navigation buttons for Create Video and Video Ledger
    assert 'id="tab-btn-studio"' in sidebar_html
    assert 'id="tab-btn-ledger"' in sidebar_html


def test_ui_generate_clears_prompt_and_queues_with_request_id():
    """Verify quickTestProduceFromPrompt clears the text box, shows Request Queued with ID, and navigates to ledger."""
    from pathlib import Path
    prompt_gen_js = Path("src/static/js/prompt_generator.js").read_text(encoding="utf-8")
    ledger_html = Path("src/templates/components/tabs/ledger.html").read_text(encoding="utf-8")

    # Banner element in ledger template
    assert 'id="ledger-queued-banner"' in ledger_html
    assert 'id="banner-request-id"' in ledger_html
    assert 'id="banner-request-detail"' in ledger_html

    # Clear prompt text box in JavaScript
    assert 'promptInput.value = ""' in prompt_gen_js
    assert 'urlInput.value = ""' in prompt_gen_js

    # Message saying Request Queued with Request ID
    assert 'title: "Request Queued"' in prompt_gen_js
    assert 'Request is queued with Request ID: ${uniqueJobId}' in prompt_gen_js

    # Updates banner and redirects to ledger
    assert 'banner.classList.remove("hidden")' in prompt_gen_js
    assert 'switchTab("ledger")' in prompt_gen_js
    assert 'renderStudioVideoHistory()' in prompt_gen_js
    assert 'selectLedgerVideo(newId)' in prompt_gen_js
