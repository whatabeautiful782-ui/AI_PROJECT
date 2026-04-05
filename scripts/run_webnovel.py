#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

MEMORY_FILES = {
    "story_state_summary": "memory/story_state_summary.md",
    "characters_summary": "memory/characters_summary.md",
    "timeline_summary": "memory/timeline_summary.md",
}

PROJECT_FILES = {
    "protocol": "protocol.md",
    "workflow": "workflow.md",
}

SKILL_FILES = {
    "idea_generator": "skills/idea_generator.md",
    "plot_designer": "skills/plot_designer.md",
    "episode_writer": "skills/episode_writer.md",
    "editor": "skills/editor.md",
}


def read_text_file(relative_path: str) -> str:
    path = REPO_ROOT / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"필수 파일이 없습니다: {relative_path}")
    return path.read_text(encoding="utf-8").strip()


def load_files(file_map: dict[str, str]) -> dict[str, str]:
    loaded = {}
    for name, relative_path in file_map.items():
        loaded[name] = read_text_file(relative_path)
    return loaded


def extract_bullets(text: str, limit: int = 5) -> list[str]:
    bullets = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
        if len(bullets) >= limit:
            break
    return bullets


def format_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def build_shared_rules(project_docs: dict[str, str]) -> str:
    protocol_rules = extract_bullets(project_docs["protocol"], limit=5)
    workflow_rules = extract_bullets(project_docs["workflow"], limit=5)
    lines = [
        "[공통 규칙]",
        "- protocol.md 기준 기본 원칙과 작업 원칙을 따른다.",
        "- workflow.md 기준으로 idea_generator -> plot_designer -> episode_writer -> editor 순서를 유지한다.",
    ]
    if protocol_rules:
        lines.append("- protocol.md 요약:")
        lines.extend(f"  - {rule}" for rule in protocol_rules)
    if workflow_rules:
        lines.append("- workflow.md 요약:")
        lines.extend(f"  - {rule}" for rule in workflow_rules)
    return "\n".join(lines)


def build_memory_snapshot(memory_docs: dict[str, str]) -> dict[str, list[str]]:
    return {
        "story": extract_bullets(memory_docs["story_state_summary"], limit=5),
        "characters": extract_bullets(memory_docs["characters_summary"], limit=6),
        "timeline": extract_bullets(memory_docs["timeline_summary"], limit=5),
    }


def call_llm_placeholder(stage_name: str, prompt: str, example_output: str) -> dict[str, str]:
    # TODO: 여기를 실제 LLM API 호출로 교체한다.
    return {
        "stage": stage_name,
        "status": "placeholder",
        "prompt": prompt,
        "output": example_output.strip(),
    }


def run_idea_generator(
    memory_docs: dict[str, str],
    project_docs: dict[str, str],
    skill_docs: dict[str, str],
) -> dict[str, str]:
    snapshot = build_memory_snapshot(memory_docs)
    prompt = f"""
[stage] idea_generator
{build_shared_rules(project_docs)}

[skill guide]
{skill_docs["idea_generator"]}

[memory summary]
story_state_summary.md
{format_bullets(snapshot["story"])}

characters_summary.md
{format_bullets(snapshot["characters"])}

timeline_summary.md
{format_bullets(snapshot["timeline"])}
""".strip()

    example_output = """
### Idea 1
- 핵심 사건: 한태현이 형을 직접 떠보며 검은 반지의 출처를 묻는 자리에서 서로의 의심이 더 노골적으로 드러난다.
- 갈등: 형은 대답을 피하고, 태현은 확신 없이 더 깊이 파고들지 말지 판단해야 한다.
- 감정 변화: 억눌린 의심이 더 선명해지지만, 형을 완전히 끊어내지 못하는 감정도 함께 커진다.
- 다음 화 연결 포인트: 형이 반지와 관련된 단서를 일부러 감춘 정황이 남는다.

### Idea 2
- 핵심 사건: 라이벌이 태현에게 반지에 대해 아는 듯한 말을 던지며 형보다 먼저 진실에 닿을 수 있다고 유혹한다.
- 갈등: 태현은 라이벌의 정보를 활용하고 싶지만, 그의 의도를 믿을 수 없다.
- 감정 변화: 형에 대한 의심은 커지고, 라이벌에 대한 경계도 동시에 짙어진다.
- 다음 화 연결 포인트: 라이벌이 형과 조직 내부 사건을 연결하는 더 큰 떡밥을 남긴다.

### Idea 3
- 핵심 사건: 조직 내부에서 형의 수상한 움직임이 포착되고, 태현은 반지와 조직 사건이 연결됐을 가능성을 체감한다.
- 갈등: 태현은 직접 증거를 좇을지, 형을 계속 관찰할지 선택해야 한다.
- 감정 변화: 단순한 가족 문제였던 의심이 조직 전체를 흔드는 위협으로 확장된다.
- 다음 화 연결 포인트: 형이 태현의 추적을 이미 눈치챈 듯한 신호가 나온다.

[TODO]
- 실제 LLM 호출 시 위 초안 대신 모델이 아이디어 3개를 생성해야 한다.
- 현재는 memory/protocol/workflow/skill 내용을 반영한 예시 출력만 반환한다.
"""
    result = call_llm_placeholder("idea_generator", prompt, example_output)
    result["selected_idea"] = "Idea 1"
    return result


def run_plot_designer(
    idea_result: dict[str, str],
    memory_docs: dict[str, str],
    project_docs: dict[str, str],
    skill_docs: dict[str, str],
) -> dict[str, str]:
    snapshot = build_memory_snapshot(memory_docs)
    prompt = f"""
[stage] plot_designer
{build_shared_rules(project_docs)}

[skill guide]
{skill_docs["plot_designer"]}

[selected idea]
{idea_result["selected_idea"]}

[idea output]
{idea_result["output"]}

[memory summary]
story_state_summary.md
{format_bullets(snapshot["story"])}

characters_summary.md
{format_bullets(snapshot["characters"])}

timeline_summary.md
{format_bullets(snapshot["timeline"])}
""".strip()

    example_output = """
### Hook
- 사건: 태현이 형을 마주한 자리에서 검은 반지를 직접 언급하며 반응을 살핀다.
- 중심 인물: 한태현, 한지훈
- 감정 변화: 태현의 의심이 시험 단계에서 직접 충돌 단계로 이동한다.

### Conflict
- 사건: 형은 답을 피한 채 태현이 더 이상 묻지 못하도록 압박하고, 태현은 침착함을 유지하며 빈틈을 찾는다.
- 중심 인물: 한태현, 한지훈
- 감정 변화: 형을 향한 분노와 애착이 동시에 흔들린다.

### Twist
- 사건: 라이벌이 개입해 반지가 조직 내부 사건과 연결됐다는 듯한 말을 던지고, 형의 침묵이 더 수상해진다.
- 중심 인물: 한태현, 라이벌, 한지훈
- 감정 변화: 태현의 시선이 가족 문제에서 조직 전체의 음모로 확장된다.

### Cliffhanger
- 사건: 형이 태현에게 더 이상 선을 넘지 말라고 경고하지만, 그 말이 오히려 반지의 위험성을 증명하는 신호처럼 들린다.
- 중심 인물: 한태현, 한지훈
- 감정 변화: 태현은 멈춰야 한다는 경고를 들을수록 더 파고들 결심을 굳힌다.
- 다음 화 연결 포인트: 형이 이미 태현의 추적을 알고 있었다는 암시를 남긴다.

[TODO]
- 실제 LLM 호출 시 선택된 아이디어 1개를 바탕으로 회차 구조를 더 정교하게 설계해야 한다.
"""
    return call_llm_placeholder("plot_designer", prompt, example_output)


def run_episode_writer(
    plot_result: dict[str, str],
    memory_docs: dict[str, str],
    project_docs: dict[str, str],
    skill_docs: dict[str, str],
) -> dict[str, str]:
    snapshot = build_memory_snapshot(memory_docs)
    prompt = f"""
[stage] episode_writer
{build_shared_rules(project_docs)}

[skill guide]
{skill_docs["episode_writer"]}

[plot]
{plot_result["output"]}

[memory summary]
story_state_summary.md
{format_bullets(snapshot["story"])}

characters_summary.md
{format_bullets(snapshot["characters"])}

timeline_summary.md
{format_bullets(snapshot["timeline"])}
""".strip()

    example_output = """
[회차 초안 placeholder]
태현은 형의 짧은 시선을 놓치지 않는다. 검은 반지를 입에 올린 순간, 방 안의 공기가 한 번 가라앉는다.

형은 대답 대신 질문을 되돌린다. 태현은 감정을 드러내지 않으려 하지만, 형이 무언가를 숨기고 있다는 확신은 더 짙어진다.

그때 라이벌이 끼어들어 반지가 단순한 장신구가 아니라는 듯한 말을 던진다. 태현은 새로운 실마리를 얻는 대신 더 큰 혼란에 빠진다.

마지막에 형은 선을 넘지 말라고 경고한다. 하지만 그 경고는 태현에게 멈추라는 말이 아니라, 반드시 확인해야 할 진실이 있다는 증거처럼 남는다.

[TODO]
- 실제 LLM 호출 시 위 placeholder를 연재 가능한 본문 초안으로 확장한다.
- Hook -> Conflict -> Twist -> Cliffhanger 흐름을 자연스럽게 연결한다.
"""
    return call_llm_placeholder("episode_writer", prompt, example_output)


def run_editor(
    episode_result: dict[str, str],
    memory_docs: dict[str, str],
    project_docs: dict[str, str],
    skill_docs: dict[str, str],
) -> dict[str, str]:
    snapshot = build_memory_snapshot(memory_docs)
    prompt = f"""
[stage] editor
{build_shared_rules(project_docs)}

[skill guide]
{skill_docs["editor"]}

[episode draft]
{episode_result["output"]}

[memory summary]
story_state_summary.md
{format_bullets(snapshot["story"])}

characters_summary.md
{format_bullets(snapshot["characters"])}

timeline_summary.md
{format_bullets(snapshot["timeline"])}
""".strip()

    example_output = """
### 수정본
[placeholder]
현재는 실제 편집 대신 episode_writer 결과를 기반으로 한 최소 수정본 자리만 반환한다.
실제 LLM 연결 후에는 문장 흐름, 감정선, 클리프행어 강화를 반영한 최종 본문이 들어가야 한다.

### 검수 메모
- 수정한 핵심 포인트: TODO - 실제 편집 결과를 바탕으로 작성
- 발견한 설정/일관성 문제: 현재 placeholder 단계에서는 없음
- 다음 단계(memory update) 반영 포인트: 형의 경고, 반지의 위험성 암시, 태현의 추적 의지 강화
"""
    return call_llm_placeholder("editor", prompt, example_output)


def print_stage_result(result: dict[str, str]) -> None:
    title = result["stage"]
    print("=" * 80)
    print(title)
    print("=" * 80)
    print(f"status: {result['status']}")
    print(result["output"])
    print()


def main() -> None:
    memory_docs = load_files(MEMORY_FILES)
    project_docs = load_files(PROJECT_FILES)
    skill_docs = load_files(SKILL_FILES)

    idea_result = run_idea_generator(memory_docs, project_docs, skill_docs)
    plot_result = run_plot_designer(idea_result, memory_docs, project_docs, skill_docs)
    episode_result = run_episode_writer(plot_result, memory_docs, project_docs, skill_docs)
    editor_result = run_editor(episode_result, memory_docs, project_docs, skill_docs)

    print_stage_result(idea_result)
    print_stage_result(plot_result)
    print_stage_result(episode_result)
    print_stage_result(editor_result)


if __name__ == "__main__":
    main()
