import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform, ScrollView, ActivityIndicator, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { auth } from '@/services/api';
import { saveTokens, saveUser } from '@/services/storage';

export default function RegisterScreen() {
  const router = useRouter();
  const [fullName, setFullName] = useState('Ana Tavares');
  const [email, setEmail] = useState('ana.tavares@email.ao');
  const [phone, setPhone] = useState('936 327 119');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [acceptedTerms, setAcceptedTerms] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    setLoading(true);
    try {
      const result = await auth.register({
        nome: fullName,
        email,
        telefone: phone,
        password,
      });
      const { access, refresh } = result.tokens;
      await saveTokens(access, refresh);
      await saveUser({ nome: fullName, email, telefone: phone });
      router.replace('/preferences');
    } catch (error: any) {
      Alert.alert('Erro', error?.response?.data?.detail || 'Falha ao criar conta. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToLogin = () => {
    router.replace('/login');
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        <ScrollView contentContainerStyle={{ flexGrow: 1 }} keyboardShouldPersistTaps="handled">
          {/* Header Row */}
          <View style={styles.header}>
            <TouchableOpacity onPress={handleBackToLogin} style={styles.backButton}>
              <MaterialCommunityIcons name="arrow-left" size={24} color="#4A4557" />
            </TouchableOpacity>
            <Text style={styles.headerTitle}>Criar conta</Text>
          </View>

          {/* Form Content */}
          <View style={styles.content}>
            <Text style={styles.subtitle}>Junte-se a milhares de estudantes em Angola.</Text>

            {/* Nome Input */}
            <Text style={styles.inputLabel}>Nome completo</Text>
            <View style={styles.inputContainer}>
              <MaterialCommunityIcons name="account-outline" size={20} color="#9A93AD" />
              <TextInput
                style={styles.textInput}
                placeholder="Introduza o seu nome"
                placeholderTextColor="#8B8598"
                value={fullName}
                onChangeText={setFullName}
              />
            </View>

            {/* Email Input */}
            <Text style={styles.inputLabel}>Email</Text>
            <View style={styles.inputContainer}>
              <MaterialCommunityIcons name="email-outline" size={20} color="#9A93AD" />
              <TextInput
                style={styles.textInput}
                placeholder="exemplo@email.ao"
                placeholderTextColor="#8B8598"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
              />
            </View>

            {/* Telemóvel Input */}
            <Text style={styles.inputLabel}>Telemóvel</Text>
            <View style={styles.inputContainer}>
              <Text style={styles.phonePrefix}>+244</Text>
              <TextInput
                style={styles.textInput}
                placeholder="999 999 999"
                placeholderTextColor="#8B8598"
                value={phone}
                onChangeText={setPhone}
                keyboardType="phone-pad"
              />
            </View>

            {/* Password Input */}
            <Text style={styles.inputLabel}>Palavra-passe</Text>
            <View style={styles.inputContainer}>
              <MaterialCommunityIcons name="lock-outline" size={20} color="#9A93AD" />
              <TextInput
                style={[styles.textInput, { flex: 1 }]}
                placeholder="Mínimo 6 caracteres"
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

            {/* Terms and conditions Checkbox */}
            <TouchableOpacity 
              style={styles.termsContainer} 
              onPress={() => setAcceptedTerms(!acceptedTerms)}
            >
              <View style={[styles.checkbox, acceptedTerms ? styles.checkboxActive : null]}>
                {acceptedTerms && <MaterialCommunityIcons name="check" size={14} color="#ffffff" />}
              </View>
              <Text style={styles.termsText}>
                Aceito os <Text style={styles.termsLink}>Termos</Text> e a <Text style={styles.termsLink}>Privacidade</Text>
              </Text>
            </TouchableOpacity>

            {/* Register Button */}
            <TouchableOpacity style={styles.submitButton} onPress={handleRegister} disabled={loading}>
              {loading ? (
                <ActivityIndicator color="#ffffff" />
              ) : (
                <Text style={styles.submitButtonText}>Criar conta</Text>
              )}
            </TouchableOpacity>

            {/* Back to Login Link */}
            <TouchableOpacity onPress={handleBackToLogin} style={styles.loginLinkContainer}>
              <Text style={styles.loginLinkLabel}>
                Já tem conta? <Text style={styles.loginLinkHighlight}>Entrar</Text>
              </Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  header: {
    height: 48,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginTop: 6,
    gap: 12,
  },
  backButton: {
    padding: 4,
  },
  headerTitle: {
    fontFamily: 'System',
    fontSize: 19,
    fontWeight: '800',
    color: '#1B1630',
  },
  content: {
    flex: 1,
    paddingHorizontal: 22,
    paddingTop: 10,
  },
  subtitle: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '500',
    color: '#8B8598',
    marginBottom: 18,
  },
  inputLabel: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '700',
    color: '#4A4557',
    marginBottom: 6,
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
    marginBottom: 13,
    gap: 11,
  },
  textInput: {
    flex: 1,
    fontFamily: 'System',
    fontSize: 14,
    color: '#1B1630',
    padding: 0,
  },
  phonePrefix: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '700',
    color: '#4A4557',
  },
  termsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginVertical: 12,
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 7,
    borderWidth: 1,
    borderColor: '#E9E5F4',
    backgroundColor: '#F5F3FB',
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkboxActive: {
    backgroundColor: '#5B18E6',
    borderColor: '#5B18E6',
  },
  termsText: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '500',
    color: '#6B6676',
  },
  termsLink: {
    color: '#5B18E6',
    fontWeight: '700',
  },
  submitButton: {
    backgroundColor: '#5B18E6',
    borderRadius: 15,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#5B18E6',
    shadowOffset: { width: 0, height: 14 },
    shadowOpacity: 0.5,
    shadowRadius: 26,
    elevation: 6,
    marginTop: 10,
    marginBottom: 16,
  },
  submitButtonText: {
    fontFamily: 'System',
    fontSize: 15,
    fontWeight: '800',
    color: '#ffffff',
  },
  loginLinkContainer: {
    alignItems: 'center',
    marginVertical: 8,
  },
  loginLinkLabel: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '600',
    color: '#8B8598',
  },
  loginLinkHighlight: {
    color: '#5B18E6',
    fontWeight: '800',
  },
});
