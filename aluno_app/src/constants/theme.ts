/**
 * Below are the colors that are used in the app. The colors are defined in the light and dark mode.
 * There are many other ways to style your app. For example, [Nativewind](https://www.nativewind.dev/), [Tamagui](https://tamagui.dev/), [unistyles](https://reactnativeunistyles.vercel.app), etc.
 */

import '@/global.css';

import { Platform } from 'react-native';

export const Colors = {
  light: {
    text: '#1B1630',
    background: '#ffffff',
    backgroundElement: '#F5F3FB',
    backgroundSelected: '#EDE7FE',
    textSecondary: '#8B8598',
    brandPurple: '#4711C4',
    accentPurple: '#5B18E6',
    lightPurpleBg: '#EDE7FE',
    darkText: '#1B1630',
    greyText: '#8B8598',
    greenAccent: '#159B5E',
    greenBg: '#DDF3E8',
    inputBg: '#F5F3FB',
    inputBorder: '#E9E5F4',
  },
  dark: {
    text: '#ffffff',
    background: '#121212',
    backgroundElement: '#1E1E1E',
    backgroundSelected: '#2D2D2D',
    textSecondary: '#A0A0A0',
    brandPurple: '#4711C4',
    accentPurple: '#5B18E6',
    lightPurpleBg: '#1E1430',
    darkText: '#ffffff',
    greyText: '#A0A0A0',
    greenAccent: '#159B5E',
    greenBg: '#1B3D2B',
    inputBg: '#1E1E1E',
    inputBorder: '#2D2D2D',
  },
} as const;

export type ThemeColor = keyof typeof Colors.light & keyof typeof Colors.dark;

export const Fonts = Platform.select({
  ios: {
    /** iOS `UIFontDescriptorSystemDesignDefault` */
    sans: 'system-ui',
    /** iOS `UIFontDescriptorSystemDesignSerif` */
    serif: 'ui-serif',
    /** iOS `UIFontDescriptorSystemDesignRounded` */
    rounded: 'ui-rounded',
    /** iOS `UIFontDescriptorSystemDesignMonospaced` */
    mono: 'ui-monospace',
  },
  default: {
    sans: 'normal',
    serif: 'serif',
    rounded: 'normal',
    mono: 'monospace',
  },
  web: {
    sans: 'var(--font-display)',
    serif: 'var(--font-serif)',
    rounded: 'var(--font-rounded)',
    mono: 'var(--font-mono)',
  },
});

export const Spacing = {
  half: 2,
  one: 4,
  two: 8,
  three: 16,
  four: 24,
  five: 32,
  six: 64,
} as const;

export const BottomTabInset = Platform.select({ ios: 50, android: 80 }) ?? 0;
export const MaxContentWidth = 800;
