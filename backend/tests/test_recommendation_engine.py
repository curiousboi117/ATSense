import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import recommendation_engine


def test_openai_fenced_json_response(monkeypatch):
    class MockResponse:
        status_code = 200

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": '```json\n["Improve your project metrics"]\n```'
                        }
                    }
                ]
            }

    def mock_post(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(recommendation_engine.requests, "post", mock_post)

    result = recommendation_engine.get_openai_suggestions(
        "test-key",
        "resume text",
        "",
        [],
    )

    assert result == ["Improve your project metrics"]
