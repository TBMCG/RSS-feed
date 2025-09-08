# Company News Dashboard - Style Guide

## Overview
This style guide defines the design system and UI standards for the Company News Dashboard application. It ensures consistency across all components and provides a modern, professional user interface aligned with Material Design principles.

## Core Design Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **UI Framework** | Material-UI v5.15.11 | Component library and design system |
| **Build Tool** | Vite | Fast build tool and development server |
| **Styling Approach** | MUI sx prop + theme | Consistent, theme-based styling |
| **Font Family** | Inter, Roboto, Helvetica, Arial | Modern, clean typography |
| **Icon Library** | @mui/icons-material | Consistent iconography |

## Color Palette

### Primary Colors

```javascript
const colors = {
  // Primary - Modern Slate Blue
  primary: {
    main: '#6366f1',
    light: '#a5b4fc',
    dark: '#4338ca',
  },

  // Secondary - Sky Blue
  secondary: {
    main: '#0ea5e9',
    light: '#7dd3fc',
    dark: '#0369a1',
  },

  // Success - Emerald
  success: {
    main: '#10b981',
    light: '#6ee7b7',
    dark: '#047857',
  },

  // Accent - Purple
  accent: {
    main: '#8b5cf6',
    light: '#c4b5fd',
    dark: '#7c3aed',
  },

  // Neutrals
  gray: {
    main: '#6b7280',
    light: '#f9fafb',
    dark: '#374151',
  },

  // Backgrounds
  background: {
    default: '#f9fafb',
    paper: '#ffffff',
  }
}
```

### Color Usage Guidelines

- **Primary**: Main brand color, used for primary actions and key UI elements
- **Secondary**: Supporting color for secondary actions and accents
- **Success**: Positive states, confirmations, and successful operations
- **Accent**: Highlights and special emphasis
- **Gray**: Text, borders, and neutral UI elements
- **Background**: Page and component backgrounds

## Typography System

### Font Configuration

```javascript
typography: {
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  h1: { 
    fontWeight: 700,
    fontSize: '2.5rem',
    lineHeight: 1.2,
  },
  h2: { 
    fontWeight: 700,
    fontSize: '2rem',
    lineHeight: 1.3,
  },
  h3: { 
    fontWeight: 600,
    fontSize: '1.75rem',
    lineHeight: 1.4,
  },
  h4: { 
    fontWeight: 600,
    fontSize: '1.5rem',
    lineHeight: 1.4,
  },
  h5: { 
    fontWeight: 600,
    fontSize: '1.25rem',
    lineHeight: 1.5,
  },
  h6: { 
    fontWeight: 600,
    fontSize: '1rem',
    lineHeight: 1.5,
  },
  button: {
    textTransform: 'none',
    fontWeight: 600,
  }
}
```

### Typography Usage

- **H1**: Page titles and main headings
- **H2**: Section headings
- **H3**: Subsection headings
- **H4-H6**: Component headings and labels
- **Body**: Regular content text
- **Button**: CTA and interactive elements

## Component Styles

### Cards

```javascript
card: {
  borderRadius: 16,
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
  border: '1px solid rgba(99, 102, 241, 0.1)',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    boxShadow: '0 8px 30px rgba(99, 102, 241, 0.15)',
    transform: 'translateY(-2px)',
  }
}
```

### Buttons

```javascript
button: {
  borderRadius: 12,
  textTransform: 'none',
  fontWeight: 600,
  padding: '10px 24px',
  boxShadow: 'none',
  '&:hover': {
    boxShadow: '0 4px 15px rgba(99, 102, 241, 0.25)',
  },
  // Contained variant
  contained: {
    boxShadow: '0 2px 8px rgba(99, 102, 241, 0.25)',
    '&:hover': {
      boxShadow: '0 6px 20px rgba(99, 102, 241, 0.35)',
      transform: 'translateY(-1px)',
    }
  }
}
```

### Papers

```javascript
paper: {
  borderRadius: 12,
  boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)',
}
```

### AppBar

```javascript
appBar: {
  backgroundColor: '#6366f1',
  boxShadow: '0 2px 12px rgba(99, 102, 241, 0.15)',
}
```

## Layout Patterns

### Responsive Breakpoints

| Breakpoint | Value | Device Type |
|------------|-------|-------------|
| xs | 0px | Mobile |
| sm | 600px | Tablet |
| md | 900px | Small Desktop |
| lg | 1200px | Desktop |
| xl | 1536px | Large Desktop |

### Container Spacing

```javascript
// Standard container padding
containerPadding: {
  py: { xs: 2, sm: 3, md: 4 },
  px: { xs: 2, sm: 3 }
}

// Section spacing
sectionSpacing: {
  mb: 3,  // Between sections
  gap: 3  // Grid gaps
}
```

### Drawer Widths

```javascript
drawerWidth: {
  desktop: 240,
  tablet: 280,
  mobile: '100%'
}
```

## Special Effects

### Gradients

```javascript
// Background gradient
backgroundGradient: 'linear-gradient(135deg, #f0f9ff 0%, rgba(165, 180, 252, 0.05) 100%)'

// Text gradient (branding)
textGradient: {
  background: 'linear-gradient(135deg, rgba(125, 211, 252, 1) 0%, rgba(110, 231, 183, 1) 100%)',
  backgroundClip: 'text',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
}
```

### Hover Effects

```javascript
// Standard hover
hoverEffect: {
  '&:hover': {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
  }
}

// Navigation hover
navHover: {
  '&:hover': {
    transform: 'translateX(4px)',
    '& .MuiListItemIcon-root': {
      transform: 'scale(1.1)',
    }
  }
}
```

### Transitions

```javascript
transitions: {
  default: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  hover: 'all 0.2s ease-in-out',
  transform: 'transform 0.2s ease-in-out'
}
```

## Form Styling

### Form Container

```javascript
formContainer: {
  maxWidth: 500,
  padding: 3,
  '& .MuiTextField-root': {
    borderRadius: 12
  }
}

// Form spacing
formSpacing: {
  stack: 3,
  buttonGap: 2
}
```

## Data Visualization

### Chart Colors

```javascript
chartColors: [
  '#6366f1',  // Primary blue
  '#06b6d4',  // Cyan
  '#e0f2fe',  // Light cyan
  '#a5b4fc',  // Light blue
  '#67e8f9',  // Light cyan
]

// Chart container
chartContainer: {
  height: '100%',
  position: 'relative',
  '& canvas': {
    borderRadius: 8
  }
}
```

## Mobile Optimizations

### Touch Targets

```javascript
touchTarget: {
  minHeight: 44,
  minWidth: 44
}
```

### Mobile Adjustments

```javascript
mobileStyles: {
  // Reduced padding
  padding: { xs: 1, sm: 2 },
  // Smaller fonts
  fontSize: { xs: '0.75rem', sm: '0.875rem' },
  // Full width elements
  width: { xs: '100%', sm: 'auto' }
}
```

## Loading States

### Loading Patterns

```javascript
// Global loading
backdropLoading: {
  color: '#fff',
  zIndex: (theme) => theme.zIndex.drawer + 1
}

// Inline loading
inlineLoading: {
  size: 20,
  thickness: 4
}
```

## Icon Usage

### Common Icons

```javascript
icons: {
  navigation: {
    factory: 'Factory',
    analytics: 'Analytics',
    person: 'Person',
    help: 'Help',
    menu: 'Menu'
  },
  actions: {
    edit: 'Edit',
    delete: 'Delete',
    add: 'Add',
    refresh: 'Refresh',
    settings: 'Settings'
  },
  status: {
    check: 'Check',
    cancel: 'Cancel',
    info: 'Info'
  }
}

// Icon button styling
iconButton: {
  color: '#ffffff',
  '&:hover': {
    backgroundColor: 'rgba(255, 255, 255, 0.1)'
  }
}
```

## Z-Index Scale

| Layer | Value | Usage |
|-------|-------|-------|
| appBar | 1100 | Top navigation |
| drawer | 1200 | Side navigation |
| modal | 1300 | Dialogs and modals |
| snackbar | 1400 | Toast notifications |
| tooltip | 1500 | Tooltips and popovers |

## Accessibility Standards

### Requirements
- **Minimum contrast ratio**: 4.5:1 for normal text, 3:1 for large text
- **Focus indicators**: Visible on all interactive elements
- **ARIA labels**: Required on all icon buttons
- **Semantic HTML**: Proper heading hierarchy and landmarks
- **Keyboard navigation**: Full support for all interactions

### Implementation
- Use `aria-label` for icon-only buttons
- Implement `focus-visible` for keyboard users
- Maintain logical tab order
- Provide skip links for navigation
- Include alt text for images

## Animation Timing

```javascript
animationDuration: {
  shortest: 150,
  shorter: 200,
  short: 250,
  standard: 300,
  complex: 375,
  enteringScreen: 225,
  leavingScreen: 195
}
```

## Best Practices

1. **Use theme variables** - Never hardcode colors or spacing
2. **Responsive first** - Design for mobile, enhance for desktop
3. **Touch-friendly** - Maintain 44px minimum touch targets
4. **Semantic colors** - Use primary, secondary, error, success
5. **Consistent interactions** - Apply hover states uniformly
6. **Border radius** - Use 12-16px for modern look
7. **Subtle shadows** - Layer depth without harshness
8. **Inter font** - Primary typeface for clarity
9. **Loading states** - Show progress for async operations
10. **Material Design** - Follow principles with custom enhancements

## Implementation Examples

### Basic Card Component

```jsx
<Card 
  sx={{
    borderRadius: 2,
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
    border: '1px solid rgba(99, 102, 241, 0.1)',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    '&:hover': {
      boxShadow: '0 8px 30px rgba(99, 102, 241, 0.15)',
      transform: 'translateY(-2px)',
    }
  }}
>
  <CardContent>
    {/* Content */}
  </CardContent>
</Card>
```

### Primary Button

```jsx
<Button
  variant="contained"
  sx={{
    borderRadius: 1.5,
    textTransform: 'none',
    fontWeight: 600,
    px: 3,
    py: 1.25,
    boxShadow: '0 2px 8px rgba(99, 102, 241, 0.25)',
    '&:hover': {
      boxShadow: '0 6px 20px rgba(99, 102, 241, 0.35)',
      transform: 'translateY(-1px)',
    }
  }}
>
  Click Me
</Button>
```

### Responsive Container

```jsx
<Container
  sx={{
    py: { xs: 2, sm: 3, md: 4 },
    px: { xs: 2, sm: 3 }
  }}
>
  {/* Content */}
</Container>
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-09-03 | Initial style guide creation |

## Maintenance

This style guide should be updated whenever:
- New components are added
- Design patterns change
- Accessibility requirements update
- Performance optimizations are discovered
- User feedback indicates improvements

For questions or suggestions, please contact the development team.