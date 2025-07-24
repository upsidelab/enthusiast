from django.test import override_settings

from agent.utils.functions import (
    get_config,
    merge_settings,
    nested_dict_to_list,
)


class TestNestedDictToList:
    FLAT_CONFIG = {
        "key_1": "path_1",
        "key_2": "path_2",
    }

    NESTED_CONFIG = {
        "key_1": {"key_2": "path_1"},
        "key_2": {"key_4": "path_2", "key_5": "path_3"},
    }

    def test_flat_dict_conversion(self):
        expected = [
            {"name": "key_1", "path": "path_1"},
            {"name": "key_2", "path": "path_2"},
        ]

        result = nested_dict_to_list(self.FLAT_CONFIG)

        assert result == expected

    def test_nested_dict_conversion(self):
        expected = {
            "key_1": [{"name": "key_2", "path": "path_1"}],
            "key_2": [{"name": "key_4", "path": "path_2"}, {"name": "key_5", "path": "path_3"}],
        }

        result = nested_dict_to_list(self.NESTED_CONFIG)

        assert result == expected

    def test_empty_dict(self):
        expected = {}

        result = nested_dict_to_list({})

        assert result == expected


class TestMergeSettings:
    def test_merge_settings_flat(self):
        base = {"A": "one", "B": "two"}
        extend = {"C": "three", "B": "overwritten"}
        expected = {"A": "one", "B": "overwritten", "C": "three"}

        result = merge_settings(base, extend)

        assert result == expected

    def test_merge_settings_nested(self):
        base = {
            "group1": {"A": "one"},
            "group2": {"X": "x"},
        }
        extend = {
            "group1": {"B": "two"},
            "group3": {"Z": "z"},
        }
        expected = {
            "group1": {"A": "one", "B": "two"},
            "group2": {"X": "x"},
            "group3": {"Z": "z"},
        }

        result = merge_settings(base, extend)

        assert result == expected

    def test_merge_settings_override_flat_key(self):
        base = {"A": "original", "B": "keep_me"}
        extend = {"A": "override_value"}
        expected = {"A": "override_value", "B": "keep_me"}

        result = merge_settings(base, extend)

        assert result == expected

    def test_merge_settings_override_nested_key(self):
        base = {"group1": {"A": "original_value", "B": "keep_me"}}
        extend = {"group1": {"A": "new_value"}}
        expected = {"group1": {"A": "new_value", "B": "keep_me"}}

        result = merge_settings(base, extend)

        assert result == expected


class TestGetConfig:
    @override_settings(
        AVAILABLE_AGENTS={"AgentA": "path.agent.a"},
        AVAILABLE_PROMPT_TEMPLATES={"PromptA": "path.prompt.a"},
        AVAILABLE_LLM={"LLMA": "path.llm.a"},
        AVAILABLE_LLM_CALLBACK_HANDLERS={"HandlerA": "path.handler.a"},
        AVAILABLE_AGENT_CALLBACK_HANDLERS={"AgentHandlerA": "path.agent.handler.a"},
        AVAILABLE_REPOSITORIES={"group1": {"RepoA": "path.repo.a"}},
        AVAILABLE_RETRIEVERS={"groupX": {"RetrieverA": "path.ret.a"}},
        AVAILABLE_INJECTORS={"InjA": "path.inj.a"},
        AVAILABLE_REGISTRIES={"reg": {"RegA": "path.reg.a"}},
        AVAILABLE_TOOLS={"llm": {"ToolA": "path.tool.a"}},
    )
    def test_get_config(self):
        cfg = get_config()

        assert cfg["agents"] == [{"name": "AgentA", "path": "path.agent.a"}]
        assert cfg["prompt_templates"] == [{"name": "PromptA", "path": "path.prompt.a"}]
        assert cfg["llm"] == [{"name": "LLMA", "path": "path.llm.a"}]
        assert cfg["llm_callback_handlers"] == [{"name": "HandlerA", "path": "path.handler.a"}]
        assert cfg["agent_callback_handlers"] == [{"name": "AgentHandlerA", "path": "path.agent.handler.a"}]
        assert cfg["repositories"]["group1"] == [{"name": "RepoA", "path": "path.repo.a"}]
        assert cfg["retrievers"]["groupX"] == [{"name": "RetrieverA", "path": "path.ret.a"}]
        assert cfg["injectors"] == [{"name": "InjA", "path": "path.inj.a"}]
        assert cfg["registries"]["reg"] == [{"name": "RegA", "path": "path.reg.a"}]
        assert cfg["tools"]["llm"] == [{"name": "ToolA", "path": "path.tool.a"}]
