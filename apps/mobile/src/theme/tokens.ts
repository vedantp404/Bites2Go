export const theme = {
  colors: {
    primary: '#185C42',
    background: '#FAF8F2',
    surface: '#FFFFFF',
    accent: '#DCEDE2',
    text: '#252B27',
    muted: '#58635B',
    border: '#D7DED7',
  },
  spacing: { xs: 4, sm: 8, md: 16, lg: 24, xl: 32, xxl: 48 },
  radii: { control: 12, card: 16 },
  sizing: { touchTarget: 48, contentMax: 560 },
  typography: {
    title: { fontSize: 32, lineHeight: 40, fontWeight: '600' as const },
    heading: { fontSize: 24, lineHeight: 32, fontWeight: '600' as const },
    body: { fontSize: 16, lineHeight: 24 },
    label: { fontSize: 14, lineHeight: 20, fontWeight: '500' as const },
  },
} as const;
