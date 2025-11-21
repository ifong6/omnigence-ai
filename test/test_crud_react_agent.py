# test/test_crud_react_agent.py
import unittest
from app.FinanceFlowState import FinanceAgentState
from app.finance_agent.crud_react_agent import crud_react_agent_node

class TestCrudReactAgentNode(unittest.TestCase):
    def test_create_company_basic(self):
        # 1) 準備初始 state（最細必要欄位）
        state = FinanceAgentState(
            user_input=(
                "Create a company called ABC Construction, "
                "address 123 Test Street, phone 28887890."
            ),
            session_id="test_session_crud_1",
            # 視乎你 FinanceAgentState 實際設計：
            intents=["create_company"],   # 如果有呢個 field
        )

        # 2) 呼叫 node
        new_state = crud_react_agent_node(state)

        # 3) 視乎你 node 嘅回傳方式做 assertion：
        # 情況 A：node 直接 return FinanceAgentState
        # self.assertIsNotNone(new_state.company_result)
        # self.assertEqual(new_state.company_result.name, "ABC Construction")

        # 情況 B：node 回傳 dict，俾 LangGraph merge
        # merged = state.model_copy(update=new_state)
        # self.assertIsNotNone(merged.company_result)

        # 你可以根據實際欄位改成：
        # - 有冇設置 company_id / company_name
        # - 有冇在 agent_responses["finance_agent"] 入面寫 response

if __name__ == "__main__":
    unittest.main()
