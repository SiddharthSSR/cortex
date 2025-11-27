# Neo-Brutalism Theme Implementation Progress

## ✅ Completed (Phase 1: Foundation)

### 1. Git Setup
- ✅ Pushed current bug fixes to `main` branch
- ✅ Created `feature/neo-brutalism-theme` branch
- ✅ Committed theme foundation

### 2. Theme Infrastructure
- ✅ Updated `tailwind.config.ts` with neo-brutalism colors:
  - `neo-yellow` (#FFD23F)
  - `neo-pink` (#FF006E)
  - `neo-mint` (#06D6A0)
  - `neo-black`, `neo-white`, `neo-cream`, `neo-gray`
- ✅ Added custom box shadows: `brutal`, `brutal-lg`, `brutal-sm`
- ✅ Added border widths: `3px`, `4px`
- ✅ Added letter spacing: `brutalist`

### 3. Theme Context System
- ✅ Created `ThemeContext.tsx` with:
  - `useTheme()` hook
  - `toggleTheme()` function
  - `isNeoBrutalism` and `isGlassmorphism` helpers
  - localStorage persistence
  - `data-theme` attribute on HTML element

### 4. Global Styles
- ✅ Updated `globals.css` with:
  - Theme-specific CSS variables
  - Neo-brutalism utility classes
  - `.brutal-button`, `.brutal-card`, `.brutal-input` classes
  - Theme-specific hover/active states

### 5. Layout Integration
- ✅ Wrapped app with `ThemeProvider` in `layout.tsx`

---

## 🚧 TODO (Phase 2: Component Updates)

### Priority 1: Core Components

#### 1. Add Theme Toggle Button
**Location**: `chat/page.tsx` (top bar)
**Implementation**:
```tsx
import { useTheme } from '@/app/contexts/ThemeContext';

// In component:
const { toggleTheme, isNeoBrutalism } = useTheme();

// Button in top bar:
<button onClick={toggleTheme} className="...">
  {isNeoBrutalism ? '🎨 Glass' : '⚡ Brutal'}
</button>
```

#### 2. Update MessageBubble Component
**File**: `frontend/app/components/MessageBubble.tsx`
**Changes Needed**:
- Add `useTheme()` hook
- Conditional className based on theme
- **Glassmorphism** (current):
  ```tsx
  bg-gradient-to-br from-blue-500/90 to-blue-600/90
  backdrop-blur-xl border border-white/20
  rounded-[20px] shadow-lg
  ```
- **Neo-Brutalism** (new):
  ```tsx
  bg-neo-pink border-[3px] border-black
  shadow-brutal rounded-none font-semibold
  ```

#### 3. Update ChatInput Component
**File**: `frontend/app/components/ChatInput.tsx`
**Changes Needed**:
- Conditional styling for input container
- Update agent toggle button styling
- Update send button styling
- **Neo-Brutalism Agent Button**:
  ```tsx
  brutal-button (yellow background, black border, hard shadow)
  ```

#### 4. Update Sidebar
**File**: `frontend/app/chat/page.tsx`
**Changes Needed**:
- Sidebar container:
  - Glassmorphism: `glass-morphism`
  - Neo-Brutalism: `bg-white border-r-[4px] border-black`
- New Chat button:
  - Neo-Brutalism: `brutal-button`
- Model dropdown:
  - Neo-Brutalism: `brutal-input`
- Clear Chat button:
  - Neo-Brutalism: Red variant with brutal styling

---

### Priority 2: Secondary Components

#### 5. Update CodeBlock Component
**File**: `frontend/app/components/CodeBlock.tsx`
- Remove rounded corners for neo-brutalism
- Add thick borders
- Hard shadows

#### 6. Update MarkdownRenderer
**File**: `frontend/app/components/MarkdownRenderer.tsx`
- Conditional styling for code blocks, tables, links

#### 7. Update ToolExecutionCard
**File**: `frontend/app/components/ToolExecutionCard.tsx`
- Add theme-aware styling

---

## 📋 Implementation Guide

### Step-by-Step for Each Component:

1. **Import theme hook**:
   ```tsx
   import { useTheme } from '@/app/contexts/ThemeContext';
   const { isNeoBrutalism } = useTheme();
   ```

2. **Create conditional className**:
   ```tsx
   const bubbleClass = isNeoBrutalism
     ? "bg-neo-pink border-[3px] border-black shadow-brutal"
     : "bg-gradient-to-br from-blue-500/90 backdrop-blur-xl";
   ```

3. **Apply to elements**:
   ```tsx
   <div className={bubbleClass}>...</div>
   ```

---

## 🎨 Neo-Brutalism Design Reference

### Colors
- **User Messages**: `bg-neo-pink` (#FF006E)
- **Assistant Messages**: `bg-white`
- **Buttons**: `bg-neo-yellow` (#FFD23F)
- **Success States**: `bg-neo-mint` (#06D6A0)
- **Borders**: Always `border-black` (3-4px)
- **Background**: `bg-neo-cream` (#FFFEF2)

### Shadows
- Default: `shadow-brutal` (6px 6px 0 #000)
- Large: `shadow-brutal-lg` (8px 8px 0 #000)
- Small: `shadow-brutal-sm` (4px 4px 0 #000)

### Typography
- Font weight: `font-bold` or `font-semibold`
- Buttons/Labels: `uppercase tracking-brutalist`
- No gradients, no blur, no transparency

### Borders
- All elements: `border-[3px] border-black`
- Rounded corners: `rounded-none` or max `rounded-lg`

### Interactions
- Hover: Increase shadow + translateY(-2px)
- Active: Decrease shadow + translateY(2px)
- Focus: Change border color to accent

---

## 🚀 Next Steps

1. **Add theme toggle button to top bar** (5 min)
2. **Update MessageBubble** (15 min)
3. **Update ChatInput** (15 min)
4. **Update Sidebar** (20 min)
5. **Update remaining components** (30 min)
6. **Test theme switching** (10 min)
7. **Polish and fix issues** (20 min)

**Total Estimated Time**: ~2 hours

---

## 🧪 Testing Checklist

- [ ] Theme toggles correctly
- [ ] Theme persists after page refresh
- [ ] All components render in both themes
- [ ] No console errors
- [ ] Responsive on mobile
- [ ] Dark mode support (glassmorphism only)
- [ ] Smooth transitions between themes
- [ ] localStorage working correctly

---

## 📝 Notes

- The glassmorphism theme is the default
- Theme preference is saved to localStorage as `cortex-theme`
- HTML element gets `data-theme` attribute for CSS targeting
- All neo-brutalism styles are scoped with `[data-theme="neo-brutalism"]`
- Can switch themes at runtime without page reload

---

## 🔗 Related Files

- `frontend/tailwind.config.ts` - Color palette
- `frontend/app/contexts/ThemeContext.tsx` - Theme state management
- `frontend/app/globals.css` - Theme-specific styles
- `frontend/app/layout.tsx` - ThemeProvider wrapper
- All component files need updates

---

## 🎯 Final Goal

A seamless theme switcher that:
1. Preserves user preference
2. Applies consistently across all components
3. Maintains accessibility
4. Provides smooth visual transitions
5. Showcases both elegant glassmorphism and bold neo-brutalism
