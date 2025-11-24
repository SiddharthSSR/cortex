# Cortex - MLX-based AI Platform TODO

## Project Status: Backend Complete (LLM + Tools + Agents) ✅

---

## Phase 1: Project Setup & Planning ✅
- [x] Research MLX-LM latest documentation (v0.28.3)
- [x] Research frontend frameworks for 2025
- [x] Create project plan and architecture
- [x] Create TODO.md file
- [x] Finalize tech stack with user
- [x] Initialize project structure

---

## Phase 2: Backend Development (MLX-LM)
### 2.1 Backend Foundation ✅
- [x] Set up Python virtual environment
- [x] Install MLX-LM and dependencies
- [x] Set up FastAPI project structure
- [x] Create requirements.txt with pinned versions
- [x] Configure CORS for frontend communication

### 2.2 Core Model Interface (Extensible Design) ✅
- [x] Design abstract BaseModel interface
- [x] Implement LLMModel class for mlx-lm
- [x] Create model configuration system
- [x] Implement model loading and caching
- [x] Add model health check endpoints

### 2.3 LLM Endpoints ✅
- [x] Create `/api/models` - list available models
- [x] Create `/api/chat` - synchronous chat endpoint
- [x] Create `/api/chat/stream` - WebSocket streaming endpoint
- [x] Implement proper error handling
- [x] Add request validation with Pydantic

### 2.4 Tools & Function Calling System ✅
- [x] Design tool registry and schema system
- [x] Implement function calling parser for model outputs
- [x] Create built-in tools:
  - [x] Web search tool (DuckDuckGo)
  - [x] Calculator tool (SymPy-based)
  - [x] Python REPL tool (sandboxed execution)
  - [x] Code generator tool (LLM-powered)
  - [ ] File system operations (read/write/list)
  - [ ] API request tool (HTTP client)
- [x] Create tool execution engine with safety checks
- [x] Implement tool result formatting for LLM context
- [x] Add tool enable/disable configuration
- [x] Create OpenAI-compatible tool definitions
- [ ] Create tool permission system

### 2.5 Agent System ✅
- [x] Design agent architecture (ReAct pattern)
- [x] Implement agent orchestration layer
- [x] Create ReAct agent with:
  - [x] Multi-step reasoning
  - [x] Tool usage and composition
  - [x] Self-correction capabilities
  - [x] Goal-oriented problem solving
- [x] Build agent memory system (execution history tracking)
- [x] Implement agent state management
- [x] Add agent observability and logging (full execution traces)
- [x] Create planning endpoint for task breakdown
- [x] Enhance ReAct prompt with explicit examples and formatting
- [ ] Create specialized agent types (code generation, research, data analysis)
- [ ] Create agent chain/workflow system
- [ ] Implement agent fallback and error recovery
- [ ] Create agent evaluation metrics

### 2.6 Backend Testing & Optimization
- [x] Test model loading and inference
- [x] Test tool execution and function calling
- [x] Test agent workflows (basic scenarios)
- [x] Create API documentation (OpenAPI/Swagger auto-generated)
- [ ] Optimize memory usage
- [ ] Add comprehensive logging and monitoring
- [ ] Performance testing and benchmarking
- [ ] Advanced agent workflow testing

---

## Phase 3: Frontend Development
### 3.1 Frontend Foundation
- [ ] Initialize Next.js 15 project with TypeScript
- [ ] Set up Tailwind CSS
- [ ] Configure project structure (components, pages, utils)
- [ ] Set up environment variables
- [ ] Configure API client

### 3.2 Chat UI Components
- [ ] Create main chat interface layout
- [ ] Build message component (user/assistant)
- [ ] Build input component with textarea
- [ ] Create model selector dropdown
- [ ] Add loading states and animations
- [ ] Implement markdown rendering for responses
- [ ] Create code block with syntax highlighting

### 3.3 Tools & Agents UI
- [ ] Create tool execution indicator/status
- [ ] Display tool calls and results in chat
- [ ] Build tool selector/configurator panel
- [ ] Add tool execution logs viewer
- [ ] Create agent mode toggle
- [ ] Display agent thinking process (chain-of-thought)
- [ ] Show agent task breakdown and progress
- [ ] Implement agent workflow visualization

### 3.4 WebSocket Integration
- [ ] Set up WebSocket client
- [ ] Implement streaming message display
- [ ] Handle streaming tool execution updates
- [ ] Stream agent thinking process
- [ ] Handle connection errors and reconnection
- [ ] Add typing indicators
- [ ] Implement message history management

### 3.5 Frontend Features
- [ ] Add conversation history (local storage)
- [ ] Implement clear chat functionality
- [ ] Add copy message to clipboard
- [ ] Create settings panel (temperature, max tokens, etc.)
- [ ] Add tool permissions management UI
- [ ] Create agent configuration interface
- [ ] Add dark/light mode toggle
- [ ] Responsive design for mobile

---

## Phase 4: Integration & Testing
- [ ] Connect frontend to backend
- [ ] End-to-end testing of chat functionality
- [ ] Test streaming responses
- [ ] Test tool execution flow
- [ ] Test agent workflows
- [ ] Test error scenarios
- [ ] Cross-browser testing
- [ ] Performance optimization

---

## Phase 5: Documentation & Deployment
- [ ] Write README.md with setup instructions
- [ ] Document API endpoints
- [ ] Create tool development guide
- [ ] Create agent development guide
- [ ] Create user guide
- [ ] Set up development environment guide
- [ ] Prepare deployment instructions

---

## Future Enhancements (Phase 6+)
### Image Models Support
- [ ] Research MLX vision models
- [ ] Design image model interface
- [ ] Implement image upload and processing
- [ ] Add image generation UI
- [ ] Create vision-based tools (image analysis, OCR)
- [ ] Add vision agents

### Audio Models Support
- [ ] Research MLX audio models
- [ ] Implement audio transcription
- [ ] Add text-to-speech capabilities
- [ ] Create audio player components
- [ ] Add audio-based tools
- [ ] Create voice-based agents

### Multimodal Models Support
- [ ] Research MLX multimodal models
- [ ] Design unified multimodal interface
- [ ] Implement multimodal input handling
- [ ] Create versatile UI for multiple modalities
- [ ] Build multimodal tools
- [ ] Create multimodal agents

### Advanced Agent Features
- [ ] Multi-agent collaboration system
- [ ] Agent-to-agent communication
- [ ] Hierarchical agent systems
- [ ] Custom agent templates
- [ ] Agent marketplace/sharing
- [ ] Agent performance analytics

### Advanced Tool Features
- [ ] Custom tool creation UI
- [ ] Tool marketplace/plugin system
- [ ] Tool composition (chaining tools)
- [ ] Tool versioning
- [ ] Community tool sharing

### Advanced Features
- [ ] Add conversation export (JSON, MD, PDF)
- [ ] Implement RAG (Retrieval Augmented Generation)
- [ ] Add fine-tuning interface
- [ ] Multi-user support with authentication
- [ ] Conversation sharing
- [ ] Model comparison mode
- [ ] Prompt templates library
- [ ] Batch processing interface

---

## Notes
- Keep architecture modular for easy addition of new model types
- Design tools and agents to be model-agnostic
- Focus on performance and user experience
- Use latest stable versions of all dependencies
- Follow best practices for security and error handling
- Implement proper sandboxing for tool execution
- Add rate limiting and safety checks for agents
