# How to Independently Test `finance_agent` Logic

This document explains how to test the **finance_agent logic in isolation**, without running the full orchestrator or HTTP server.

---

## 🧩 Overview

To properly test the finance agent, we separate testing into **three layers**:

### **Layer 1 — Unit test the Service Layer (`CompanyServiceImpl`)**
This is the most stable and recommended starting point.

Here, you test pure business logic + database operations without touching any agent or LangGraph flow.

Example: verifying that `CompanyServiceImpl.create()` correctly inserts a company into the DB.

---

### **Layer 2 — Unit test the Agent Node (`finance_agent_node`)**
Here, you test:

- The agent node correctly interprets the user request  
- The agent node calls the appropriate service  
- The agent node produces structured data for aggregation  

This does not involve the orchestrator, HTTP routes, or LangGraph graph wiring.

---

### **Layer 3 — Integration test through `orchestrator_agent_flow()`**
This runs the whole LangGraph pipeline:

1. classifier_agent  
2. intent_analyzer  
3. finance_agent  
4. aggregation_agent  

This validates whether the orchestrator correctly routes requests to the finance agent.

---

## Summary

If you want to **just** test "creating a company" inside finance_agent:

- Test `CompanyServiceImpl` (pure logic)
- Test `finance_agent_node` (agent logic)
- Optionally test `orchestrator_agent_flow` (integration level)

Each level isolates a different responsibility.
