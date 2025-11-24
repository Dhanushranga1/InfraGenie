# 🎯 Phase 2 Launch Checklist

## ✅ Pre-Launch Checklist

### 1. Clerk Setup (REQUIRED)
- [ ] Create Clerk account at https://dashboard.clerk.com
- [ ] Create new application in Clerk dashboard
- [ ] Copy Publishable Key (starts with `pk_`)
- [ ] Copy Secret Key (starts with `sk_`)
- [ ] Create `.env.local` file in frontend directory
- [ ] Add both keys to `.env.local`:
  ```env
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
  CLERK_SECRET_KEY=sk_test_xxxxx
  ```
- [ ] Configure paths in Clerk dashboard:
  - Sign-in URL: `/sign-in`
  - Sign-up URL: `/sign-up`
  - After sign-in: `/`
  - After sign-up: `/`

### 2. Backend Setup (REQUIRED)
- [ ] Backend server running at `http://localhost:8000`
- [ ] Groq API key configured in backend
- [ ] Test endpoints:
  - `POST /api/v1/generate` (returns infrastructure code)
  - `POST /api/v1/download` (returns ZIP file)

### 3. Frontend Setup
- [ ] All dependencies installed (`npm install` completed)
- [ ] No TypeScript errors (verified ✅)
- [ ] Dev server starts without errors

---

## 🧪 Testing Checklist

### Test Suite 1: Authentication
- [ ] Open incognito window → `http://localhost:3000`
- [ ] Verify redirect to `/sign-in`
- [ ] Click "Sign up" link
- [ ] Create test account (email + password)
- [ ] Verify redirect to dashboard after sign-up
- [ ] Verify UserButton appears in navbar (top-right)
- [ ] Click UserButton → Verify profile menu
- [ ] Sign out → Verify redirect to sign-in
- [ ] Sign in again → Verify dashboard access

### Test Suite 2: Chat Interface
- [ ] Sign in to dashboard
- [ ] Verify chat panel on left (350px width)
- [ ] Enter prompt: "Create an AWS EC2 instance"
- [ ] Click Send button
- [ ] Verify terminal loader appears
- [ ] Verify loader cycles through 4 messages (2s each):
  - "Architecting your infrastructure..."
  - "Validating resource configurations..."
  - "Scanning for security vulnerabilities..."
  - "Estimating deployment costs..."
- [ ] Wait for AI response
- [ ] Verify message bubbles appear (user + AI)
- [ ] Verify code blocks render correctly
- [ ] Verify auto-scroll to bottom

### Test Suite 3: Architecture Diagram
- [ ] After infrastructure generation completes
- [ ] Verify diagram appears on right panel
- [ ] Verify nodes have correct icons:
  - EC2/VM → Server icon
  - VPC/Network → Cloud icon
  - Security Group → Shield icon
  - Load Balancer → Network icon
  - Database → Database icon
- [ ] Verify nodes are auto-arranged (not overlapping)
- [ ] Test zoom in/out (mouse wheel)
- [ ] Test pan (click + drag)
- [ ] Verify MiniMap shows in bottom-right corner
- [ ] Verify edges connect resources correctly

### Test Suite 4: Status Badges
- [ ] Look at top-right corner of diagram
- [ ] Verify **Cost Badge** appears
- [ ] Check cost amount displays (e.g., "$45.30/mo")
- [ ] Verify color logic:
  - Amber background if cost > $50
  - Emerald background if cost ≤ $50
- [ ] Verify **Security Badge** appears
- [ ] Check security status:
  - "Secure" (emerald) if 0 risks
  - "X Risk(s)" (rose) if risks detected
- [ ] Verify badges have glassmorphism effect
- [ ] Verify badges float over diagram (not behind)

### Test Suite 5: Download Functionality
- [ ] Scroll to bottom of chat panel
- [ ] Verify Download button is visible
- [ ] Before generation: Verify button is disabled (gray)
- [ ] After generation: Verify button is enabled (violet gradient)
- [ ] Click "Download Deployment Kit"
- [ ] Verify button shows loading spinner
- [ ] Verify button text changes to "Preparing Download..."
- [ ] Wait for download to complete
- [ ] Verify file downloads: `infragenie-deployment-{timestamp}.zip`
- [ ] Verify ZIP file size > 0 KB
- [ ] Extract ZIP and verify contents:
  - `terraform/main.tf`
  - `ansible/playbook.yml`
  - `cost_estimate.txt`
  - `README.md`

### Test Suite 6: UI/UX Polish
- [ ] Verify dark mode colors (zinc-950 background)
- [ ] Verify violet-500 primary color (logo, accents)
- [ ] Verify JetBrains Mono font in logo/code
- [ ] Verify glassmorphism effects (backdrop-blur)
- [ ] Verify cyberpunk glow effects (violet + cyan)
- [ ] Verify dot pattern background on diagram
- [ ] Verify status bar at bottom:
  - Green pulse dot
  - "Backend Connected"
  - Model name
  - Version "Phase 2 Complete"
- [ ] Verify navbar border and styling
- [ ] Verify responsive layout (chat stays 350px)

---

## 🐛 Troubleshooting Tests

### Issue: Middleware redirect loop
- [ ] Check `.env.local` has valid Clerk keys
- [ ] Restart dev server: `npm run dev`
- [ ] Clear browser cookies/cache
- [ ] Verify middleware.ts has correct public routes

### Issue: Download fails
- [ ] Check backend is running at `http://localhost:8000`
- [ ] Test endpoint manually:
  ```bash
  curl -X POST http://localhost:8000/api/v1/download \
    -H "Content-Type: application/json" \
    -d '{"project_id":"test","terraform_code":"test","ansible_playbook":"test","cost_estimate":"$10","user_prompt":"test"}'
  ```
- [ ] Check browser console for errors
- [ ] Verify Zustand store has data

### Issue: Diagram not rendering
- [ ] Check browser console for ReactFlow errors
- [ ] Verify terraformCode in Zustand store
- [ ] Check HCL syntax is valid
- [ ] Verify dagre package installed

### Issue: Badges not showing
- [ ] Verify costEstimate exists in store
- [ ] Verify securityRisks exists in store
- [ ] Check z-index conflicts
- [ ] Inspect element to verify badges are rendered

---

## 📊 Performance Tests

- [ ] Initial page load < 2s
- [ ] Chat message response < 30s (depends on Groq)
- [ ] Diagram render < 1s
- [ ] Download ZIP < 5s
- [ ] No console errors
- [ ] No memory leaks (check DevTools Performance)

---

## 🚀 Production Readiness

### Security
- [ ] Clerk keys are in `.env.local` (not committed)
- [ ] Middleware protects all routes
- [ ] API endpoints use HTTPS (in production)
- [ ] CORS configured correctly

### Performance
- [ ] Images optimized
- [ ] Code splitting enabled (Next.js default)
- [ ] Lazy loading components (if needed)
- [ ] API response caching (TanStack Query)

### Monitoring
- [ ] Error boundaries added (future)
- [ ] Analytics tracking (future)
- [ ] Logging setup (future)

---

## ✅ Sign-Off

When all items are checked, Phase 2 is complete and ready for:
- User acceptance testing
- Beta release
- Phase 3 planning

---

**Last Updated**: Phase 2 Implementation Complete  
**Next Phase**: Phase 3 - Advanced Features  
**Status**: Ready for Launch 🚀
