import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { Stack } from 'expo-router';
import { useColorScheme } from 'react-native';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const colorScheme = useColorScheme();

  useEffect(() => {
    SplashScreen.hideAsync();
  }, []);

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <Stack screenOptions={{ headerShown: false, animation: 'fade' }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="splash" />
        <Stack.Screen name="onboarding" />
        <Stack.Screen name="login" />
        <Stack.Screen name="register" />
        <Stack.Screen name="recover" />
        <Stack.Screen name="preferences" />
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="curso/[id]" />
        <Stack.Screen name="escola/[id]" />
        <Stack.Screen name="aula/[id]" />
        <Stack.Screen name="prova/[id]" />
        <Stack.Screen name="certificado/[id]" />
        <Stack.Screen name="escolas" />
        <Stack.Screen name="favoritos" />
        <Stack.Screen name="trilhas" />
        <Stack.Screen name="checkout" />
        <Stack.Screen name="pagamento-iban" />
        <Stack.Screen name="upload-comprovativo" />
        <Stack.Screen name="downloads" />
        <Stack.Screen name="notas" />
        <Stack.Screen name="pagamentos" />
        <Stack.Screen name="configuracoes" />
        <Stack.Screen name="chat" />
        <Stack.Screen name="notificacoes" />
        <Stack.Screen name="centros-parceiros" />
        <Stack.Screen name="candidatura" />
        <Stack.Screen name="minhas-candidaturas" />
      </Stack>
    </ThemeProvider>
  );
}
