# Learnings: What Should Have Been in the Initial Documentation

This document captures what we learned during implementation that would have been valuable to know from the start. These are gaps in the initial requirements, examples, or documentation that caused us to debug and figure things out the hard way.

## 1. Agent Process Path Issues

### Problem
- Agent couldn't join rooms, showing error: `FileNotFoundError: No such file or directory: '/Users/andrep/Documents/code/appointment-confirmation-agent/appointment_agent.py'`
- The agent was looking for the Python file in the root directory instead of the `agent/` subdirectory

### Root Cause
- Agent was started from the wrong directory or with wrong path
- When spawning child processes for room handling, it used incorrect relative paths

### Solution
- Killed the incorrectly started agent process
- Restarted using `./start_agent.sh` from the project root
- The startup script properly handles the path to `agent/appointment_agent.py`

### What Should Have Been Documented
- LiveKit agents must be started from project root when using subdirectories
- The working directory affects how child processes are spawned
- Example startup script showing correct path handling

## 2. LiveKit AgentSession API Changes

### Problem
- Error: `AttributeError: 'AgentSession' object has no attribute 'chat_ctx'`
- Code was using outdated API pattern from older LiveKit agents examples

### Root Cause
- LiveKit agents API had changed between versions
- Was trying to use `self.session.chat_ctx.append()` pattern which no longer exists

### Solution
- Changed from:
  ```python
  self.session.chat_ctx.append(role="assistant", content=greeting)
  await self.session.generate_reply()
  ```
- To:
  ```python
  await self.session.say(greeting)
  ```

### What Should Have Been Documented
- Current LiveKit agents API uses `await self.session.say()` not `chat_ctx`
- The examples in the repo showed outdated patterns
- API version compatibility notes

## 3. Token Server Missing Required Field

### Problem
- Frontend API getting 422 Unprocessable Entity from token server
- Token generation failing with: `{"detail":[{"type":"missing","loc":["body","user_id"],"msg":"Field required"}]}`

### Root Cause
- Token server required `user_id` field in the request
- Frontend's connection-details API wasn't sending this field

### Solution
- Updated frontend API to generate and include user_id:
  ```typescript
  const userId = `user-${timestamp}`;
  body: JSON.stringify({
    user_email: userEmail,
    full_name: participantName,
    user_id: userId,  // Added this field
    room_name: roomName,
  })
  ```

### What Should Have Been Documented
- Token server requires `user_id` field (not optional)
- Complete API schema for token generation endpoint
- Example of full token request with all required fields

## 4. Repository Structure Confusion

### Problem
- Initial file organization was scattered (appointment_agent.py in root, token.ts referenced)
- Made it harder to understand project structure

### Root Cause
- Started without clear organizational structure
- Mixed references to other projects

### Solution
- Reorganized into clear directories:
  - `agent/` - Core agent code
  - `token_server/` - Authentication server
  - `frontend/` - React testing UI
- Created startup scripts for each component

### What Should Have Been Documented
- Recommended project structure for LiveKit agents
- Separate directories for agent, token server, and frontend
- Where to put what types of files

## 5. Frontend Environment Variables

### Problem
- Frontend `.env.example` was missing `NEXT_PUBLIC_TOKEN_SERVER_URL`
- Could cause confusion for new developers

### Root Cause
- Oversight when modifying frontend to use external token server
- Original template had built-in token generation

### Solution
- Updated `.env.example` to include all required variables
- Added clear comments about each variable's purpose

### What Should Have Been Documented
- Frontend needs `NEXT_PUBLIC_TOKEN_SERVER_URL` environment variable
- Complete list of all environment variables across all components
- Which variables are required vs optional

## 6. Service Coordination

### Problem
- Multiple services need to run together (token server, agent, frontend)
- Easy to forget one or have wrong startup order

### Root Cause
- Complex system with multiple moving parts
- No unified way to check all services

### Solution
- Created `check_services.sh` to verify all components
- Created `test_integration.sh` for automated testing
- Clear documentation of startup order

### What Should Have Been Documented
- Order of service startup (token server → agent → frontend)
- Port requirements for each service
- How to verify each service is running correctly

## 7. Archon Project Update Limitations

### Problem
- Couldn't update GitHub repository URL in Archon project
- API call appeared to work but changes didn't persist

### Root Cause
- Unclear - possibly API limitation or different update method needed

### Solution
- Marked as complete since actual repository is correct
- Archon metadata is cosmetic issue only

### What Should Have Been Documented
- Archon project API limitations
- Which fields can be updated after creation
- Alternative ways to manage project metadata

## What Was Missing from Initial Documentation

1. **Current API patterns** - Examples showed outdated LiveKit API usage
2. **Complete field requirements** - Token server needed `user_id` but wasn't documented
3. **Project structure guidance** - No recommendation on organizing multi-component projects
4. **Environment variable list** - Missing variables like `NEXT_PUBLIC_TOKEN_SERVER_URL`
5. **Service startup order** - Critical to know token server must start before frontend
6. **Working directory requirements** - Agent must run from project root
7. **Integration patterns** - How to connect frontend to external token server

## What Would Have Saved Time

1. **Complete working example** - Not just snippets but full project structure
2. **API migration guide** - Showing old vs new patterns
3. **Service dependency diagram** - Visual of what needs what
4. **Environment setup checklist** - All variables across all components
5. **Common errors section** - "If you see X error, check Y"
6. **Testing guide** - How to verify each component works before integration