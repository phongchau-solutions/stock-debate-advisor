/**
 * Material Design 3 Color System
 * Reference: https://m3.material.io/
 */

export const md3ColorScheme = {
  // Light Theme
  light: {
    primary: '#6750a4',
    onPrimary: '#ffffff',
    primaryContainer: '#eaddff',
    onPrimaryContainer: '#21005d',

    secondary: '#625b71',
    onSecondary: '#ffffff',
    secondaryContainer: '#e8def8',
    onSecondaryContainer: '#1d192b',

    tertiary: '#7d5260',
    onTertiary: '#ffffff',
    tertiaryContainer: '#ffd8e4',
    onTertiaryContainer: '#370b1e',

    error: '#b3261e',
    onError: '#ffffff',
    errorContainer: '#f9dedc',
    onErrorContainer: '#410e0b',

    background: '#fffbfe',
    onBackground: '#1c1b1f',

    surface: '#fffbfe',
    onSurface: '#1c1b1f',
    surfaceVariant: '#e7e0ec',
    onSurfaceVariant: '#49454e',

    outline: '#79747e',
    outlineVariant: '#cac7d0',

    scrim: '#000000',
    shadow: '#000000',
  },

  // Dark Theme
  dark: {
    primary: '#d0bcff',
    onPrimary: '#371e55',
    primaryContainer: '#4f378b',
    onPrimaryContainer: '#eaddff',

    secondary: '#ccc7d8',
    onSecondary: '#332d41',
    secondaryContainer: '#4a4458',
    onSecondaryContainer: '#e8def8',

    tertiary: '#f6b1d7',
    onTertiary: '#5c2d42',
    tertiaryContainer: '#73435b',
    onTertiaryContainer: '#ffd8e4',

    error: '#f2b8b5',
    onError: '#601410',
    errorContainer: '#8c1d18',
    onErrorContainer: '#f9dedc',

    background: '#1c1b1f',
    onBackground: '#e6e1e6',

    surface: '#1c1b1f',
    onSurface: '#e6e1e6',
    surfaceVariant: '#49454e',
    onSurfaceVariant: '#cac7d0',

    outline: '#95919b',
    outlineVariant: '#49454e',

    scrim: '#000000',
    shadow: '#000000',
  },
};

/**
 * Material Design 3 Typography System
 * Reference: https://m3.material.io/styles/typography/overview
 */
export const md3Typography = {
  displayLarge: {
    fontSize: '57px',
    lineHeight: '64px',
    letterSpacing: '0px',
    fontWeight: 400,
  },
  displayMedium: {
    fontSize: '45px',
    lineHeight: '52px',
    letterSpacing: '0px',
    fontWeight: 400,
  },
  displaySmall: {
    fontSize: '36px',
    lineHeight: '44px',
    letterSpacing: '0px',
    fontWeight: 400,
  },

  headlineLarge: {
    fontSize: '32px',
    lineHeight: '40px',
    letterSpacing: '0px',
    fontWeight: 400,
  },
  headlineMedium: {
    fontSize: '28px',
    lineHeight: '36px',
    letterSpacing: '0px',
    fontWeight: 400,
  },
  headlineSmall: {
    fontSize: '24px',
    lineHeight: '32px',
    letterSpacing: '0px',
    fontWeight: 400,
  },

  titleLarge: {
    fontSize: '22px',
    lineHeight: '28px',
    letterSpacing: '0px',
    fontWeight: 500,
  },
  titleMedium: {
    fontSize: '16px',
    lineHeight: '24px',
    letterSpacing: '0.15px',
    fontWeight: 500,
  },
  titleSmall: {
    fontSize: '14px',
    lineHeight: '20px',
    letterSpacing: '0.1px',
    fontWeight: 500,
  },

  bodyLarge: {
    fontSize: '16px',
    lineHeight: '24px',
    letterSpacing: '0.5px',
    fontWeight: 400,
  },
  bodyMedium: {
    fontSize: '14px',
    lineHeight: '20px',
    letterSpacing: '0.25px',
    fontWeight: 400,
  },
  bodySmall: {
    fontSize: '12px',
    lineHeight: '16px',
    letterSpacing: '0.4px',
    fontWeight: 400,
  },

  labelLarge: {
    fontSize: '14px',
    lineHeight: '20px',
    letterSpacing: '0.1px',
    fontWeight: 500,
  },
  labelMedium: {
    fontSize: '12px',
    lineHeight: '16px',
    letterSpacing: '0.5px',
    fontWeight: 500,
  },
  labelSmall: {
    fontSize: '11px',
    lineHeight: '16px',
    letterSpacing: '0.5px',
    fontWeight: 500,
  },
};

/**
 * Material Design 3 Shape System
 * Reference: https://m3.material.io/styles/shape/shape-system
 */
export const md3Shape = {
  corner: {
    none: '0px',
    extraSmall: '4px',
    small: '8px',
    medium: '12px',
    large: '16px',
    extraLarge: '28px',
    full: '50%',
  },
};

/**
 * Material Design 3 Component State System
 * Reference: https://m3.material.io/foundations/interaction/states
 */
export const md3StateOpacity = {
  hoverOpacity: 0.08,
  focusOpacity: 0.12,
  pressedOpacity: 0.12,
  draggedOpacity: 0.16,
  disabledOpacity: 0.38,
};

/**
 * Material Design 3 Elevation System
 * Reference: https://m3.material.io/styles/elevation/overview
 */
export const md3Elevation = {
  level0: 'none',
  level1: '0px 1px 3px 1px rgba(0, 0, 0, 0.15), 0px 1px 2px 0px rgba(0, 0, 0, 0.30)',
  level2: '0px 3px 6px 0px rgba(0, 0, 0, 0.15), 0px 2px 4px 0px rgba(0, 0, 0, 0.30)',
  level3: '0px 6px 10px 0px rgba(0, 0, 0, 0.15), 0px 2px 5px 0px rgba(0, 0, 0, 0.30)',
  level4: '0px 8px 12px 0px rgba(0, 0, 0, 0.15), 0px 4px 8px 0px rgba(0, 0, 0, 0.30)',
  level5: '0px 12px 16px 0px rgba(0, 0, 0, 0.15), 0px 4px 8px 0px rgba(0, 0, 0, 0.30)',
};
