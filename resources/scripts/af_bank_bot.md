```mermaid
flowchart TD
  input_conversation["input-conversation (Start)"];
  handoff_coordinator["handoff-coordinator"];
  triage_agent["triage_agent"];
  pin_agent["pin_agent"];
  card_agent["card_agent"];
  billing_agent["billing_agent"];
  handoff_user_input["handoff-user-input"];
  triage_agent_handoff_requests["triage_agent_handoff_requests"];
  handoff_coordinator --> triage_agent;
  triage_agent --> handoff_coordinator;
  handoff_coordinator --> pin_agent;
  pin_agent --> handoff_coordinator;
  handoff_coordinator --> card_agent;
  card_agent --> handoff_coordinator;
  handoff_coordinator --> billing_agent;
  billing_agent --> handoff_coordinator;
  input_conversation --> triage_agent;
  handoff_coordinator --> handoff_user_input;
  handoff_user_input --> triage_agent_handoff_requests;
  triage_agent_handoff_requests --> handoff_user_input;
  handoff_user_input --> handoff_coordinator;
  ```