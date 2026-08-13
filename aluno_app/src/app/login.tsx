import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform, ScrollView, Image, ActivityIndicator, Alert } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import logo from '../../assets/images/logo1-removebg-preview.png';
import { auth } from '@/services/api';
import { saveTokens, saveUser } from '@/services/storage';

export default function LoginScreen() {
  const router = useRouter();
  const [email, setEmail] = useState('aluno@teste.com');
  const [password, setPassword] = useState('123456');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    try {
      const { access, refresh } = await auth.login(email, password);
      await saveTokens(access, refresh);
      await saveUser({ email });
      router.replace('/(tabs)/home');
    } catch (error: any) {
      Alert.alert('Erro', error?.response?.data?.detail || 'Credenciais inválidas. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = () => {
    router.push('/recover');
  };

  const handleRegister = () => {
    router.push('/register');
  };

  return (
    <LinearGradient
      colors={['#6A28F0', '#4711C4']}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
    >
      <StatusBar style="light" />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        <ScrollView contentContainerStyle={{ flexGrow: 1 }} keyboardShouldPersistTaps="handled">
          {/* Header section with brand info */}
          <View style={styles.header}>
            <View style={styles.logoContainer}>
              <Image source={logo} style={styles.logo} resizeMode="contain" />
            </View>
            <Text style={styles.brandTitle}>EdukAngola</Text>
            <Text style={styles.brandSubtitle}>
              Aprenda, avalie-se e certifique-se.{"\n"}A educação de Angola na palma da mão.
            </Text>
          </View>

          {/* Bottom Card Form */}
          <View style={styles.formCard}>
            <Text style={styles.cardTitle}>Bem-vindo de volta</Text>
            <Text style={styles.cardSubtitle}>Entre para continuar a aprender</Text>

            {/* Email Input */}
            <View style={styles.inputContainer}>
              <MaterialCommunityIcons name="email-outline" size={20} color="#9A93AD" />
              <TextInput
                style={styles.textInput}
                placeholder="E-mail"
                placeholderTextColor="#8B8598"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
              />
            </View>

            {/* Password Input */}
            <View style={styles.inputContainer}>
              <MaterialCommunityIcons name="lock-outline" size={20} color="#9A93AD" />
              <TextInput
                style={[styles.textInput, { flex: 1 }]}
                placeholder="Palavra-passe"
                placeholderTextColor="#8B8598"
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPassword}
                autoCapitalize="none"
              />
              <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                <MaterialCommunityIcons
                  name={showPassword ? 'eye-outline' : 'eye-off-outline'}
                  size={20}
                  color="#9A93AD"
                />
              </TouchableOpacity>
            </View>

            {/* Forgot Password Link */}
            <TouchableOpacity onPress={handleForgotPassword} style={styles.forgotPasswordLink}>
              <Text style={styles.forgotPasswordText}>Esqueceu a senha?</Text>
            </TouchableOpacity>

            {/* Submit Button */}
            <TouchableOpacity style={styles.loginButton} onPress={handleLogin} disabled={loading}>
              {loading ? (
                <ActivityIndicator color="#ffffff" />
              ) : (
                <Text style={styles.loginButtonText}>Entrar</Text>
              )}
            </TouchableOpacity>

            {/* Register Link */}
            <TouchableOpacity onPress={handleRegister} style={styles.registerContainer}>
              <Text style={styles.registerText}>
                Novo aqui? <Text style={styles.registerHighlight}>Criar conta</Text>
              </Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 30,
    paddingTop: 60,
    paddingBottom: 40,
  },
  logoContainer: {
    width: 96,
    height: 96,
    borderRadius: 28,
    backgroundColor: 'rgba(255, 255, 255, 0.14)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logo: {
    width: 64,
    height: 64,
  },
  brandTitle: {
    fontFamily: 'System',
    fontSize: 27,
    fontWeight: '800',
    color: '#ffffff',
    marginTop: 22,
    letterSpacing: -0.5,
  },
  brandSubtitle: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '500',
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 22,
  },
  formCard: {
    backgroundColor: '#ffffff',
    borderTopLeftRadius: 34,
    borderTopRightRadius: 34,
    paddingHorizontal: 24,
    paddingTop: 30,
    paddingBottom: Platform.OS === 'ios' ? 40 : 30,
  },
  cardTitle: {
    fontFamily: 'System',
    fontSize: 19,
    fontWeight: '800',
    color: '#1B1630',
  },
  cardSubtitle: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '500',
    color: '#8B8598',
    marginTop: 4,
    marginBottom: 18,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F3FB',
    borderWidth: 1,
    borderColor: '#E9E5F4',
    borderRadius: 14,
    paddingHorizontal: 15,
    paddingVertical: 14,
    marginBottom: 11,
    gap: 11,
  },
  textInput: {
    flex: 1,
    fontFamily: 'System',
    fontSize: 14,
    color: '#1B1630',
    padding: 0, // Reset default Android text input padding
  },
  forgotPasswordLink: {
    alignSelf: 'flex-end',
    marginVertical: 12,
  },
  forgotPasswordText: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '700',
    color: '#5B18E6',
  },
  loginButton: {
    backgroundColor: '#5B18E6',
    borderRadius: 15,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#5B18E6',
    shadowOffset: { width: 0, height: 14 },
    shadowOpacity: 0.55,
    shadowRadius: 26,
    elevation: 6,
    marginTop: 4,
    marginBottom: 16,
  },
  loginButtonText: {
    fontFamily: 'System',
    fontSize: 15,
    fontWeight: '800',
    color: '#ffffff',
  },
  registerContainer: {
    alignItems: 'center',
    marginTop: 8,
  },
  registerText: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '600',
    color: '#8B8598',
  },
  registerHighlight: {
    color: '#5B18E6',
    fontWeight: '800',
  },
});
