export type MessageRole = 'system' | 'user' | 'assistant' | 'tool';

export interface Message {
  role: MessageRole;
  content: string;
  tool_calls?: ToolCall[];
  timestamp?: string;
  agent_steps?: AgentStep[];
}

export interface ToolCall {
  id?: string;
  tool_name: string;
  parameters: Record<string, any>;
  result?: any;
}

export interface ChatRequest {
  messages: Message[];
  model?: string;
  temperature?: number;
  max_tokens?: number;
  enable_agent?: boolean;
}

export interface ChatResponse {
  message: Message;
  model: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  agent_steps?: AgentStep[];
}

export interface AgentStep {
  step_number: number;
  thought: string;
  action: string | null;
  action_input: Record<string, any> | null;
  observation: string | null;
  status: string;
}

export interface Model {
  id: string;
  name: string;
  description?: string;
  loaded: boolean;
}

export interface Tool {
  name: string;
  description: string;
  enabled: boolean;
  parameters: Record<string, any>;
}
