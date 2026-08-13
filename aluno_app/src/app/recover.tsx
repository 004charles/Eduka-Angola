import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, TextInput, Alert, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { auth } from '@/services/api';

export default function RecoverScreen() {
  const router = useRouter();
  const [step, setStep] = useState<'email' | 'verify'>('email');
  const [email, setEmail] = useState('');
  const [pin, setPin] = useState('');
  const [nova_senha, setNovaSenha] = useState('');
  const [countdown, setCountdown] = useState(60);
  const [loadingEmail, setLoadingEmail] = useState(false);
  const [loadingVerify, setLoadingVerify] = useState(false);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setInterval(() => {
        setCountdown(countdown - 1);
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [countdown]);

  const handleSendCode = async () => {
    setLoadingEmail(true);
    try {
      await auth.esqueciSenha(email);
      setStep('verify');
      setCountdown(60);
    } catch (error: any) {
      Alert.alert('Erro', error?.response?.data?.detail || 'Falha ao enviar código. Tente novamente.');
    } finally {
      setLoadingEmail(false);
    }
  };

  const handleConfirm = async () => {
    if (pin.length !== 4) {
      Alert.alert('Erro', 'Introduza o código de 4 dígitos.');
      return;
    }
    if (nova_senha.length < 6) {
      Alert.alert('Erro', 'A nova palavra-passe deve ter pelo menos 6 caracteres.');
      return;
    }
    setLoadingVerify(true);
    try {
      await auth.redefinirSenha(email, pin, nova_senha);
      router.replace('/login');
    } catch (error: any) {
      Alert.alert('Erro', error?.response?.data?.detail || 'Código inválido ou expirado. Tente novamente.');
    } finally {
      setLoadingVerify(false);
    }
  };

  const handleBack = () => {
    if (step === 'verify') {
      setStep('email');
    } else {
      router.back();
    }
  };

  const maskedEmail = email ? `${email.charAt(0)}****@${email.split('@')[1] || ''}` : '';

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      
      {/* Header Row */}
      <View style={styles.header}>
        <TouchableOpacity onPress={handleBack} style={styles.backButton}>
          <MaterialCommunityIcons name="arrow-left" size={24} color="#4A4557" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{step === 'email' ? 'Recuperar senha' : 'Verificação'}</Text>
      </View>

      {step === 'email' ? (
        /* Step 1: Email Input */
        <View style={styles.content}>
          <View style={styles.iconBox}>
            <MaterialCommunityIcons name="lock-reset" size={40} color="#5B18E6" />
          </View>

          <Text style={styles.title}>Esqueceu a senha?</Text>
          <Text style={styles.description}>
            Introduza o seu email para receber um código{"\n"}de redefinição de senha.
          </Text>

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

          <View style={styles.footer}>
            <TouchableOpacity style={styles.confirmButton} onPress={handleSendCode} disabled={loadingEmail}>
              {loadingEmail ? (
                <ActivityIndicator color="#ffffff" />
              ) : (
                <Text style={styles.confirmButtonText}>Enviar código</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        /* Step 2: Code + New Password */
        <>
          <View style={styles.content}>
            <View style={styles.iconBox}>
              <MaterialCommunityIcons name="email-check-outline" size={40} color="#5B18E6" />
            </View>

            <Text style={styles.title}>Introduza o código</Text>
            <Text style={styles.description}>
              Enviámos um PIN de 4 dígitos para{"\n"}
              <Text style={styles.emailHighlight}>{maskedEmail}</Text>
            </Text>

            <TextInput
              style={styles.hiddenInput}
              keyboardType="number-pad"
              maxLength={4}
              value={pin}
              onChangeText={setPin}
              autoFocus
            />

            <View style={styles.pinContainer}>
              {[0, 1, 2, 3].map((i) => (
                <View key={i} style={[styles.pinBox, pin.length > i && styles.pinBoxActive]}>
                  {pin.length > i ? (
                    <Text style={styles.pinTextActive}>{pin[i]}</Text>
                  ) : (
                    <Text style={styles.pinText}>—</Text>
                  )}
                </View>
              ))}
            </View>

            <View style={styles.inputContainer}>
              <MaterialCommunityIcons name="lock-outline" size={20} color="#9A93AD" />
              <TextInput
                style={styles.textInput}
                placeholder="Nova palavra-passe (mín. 6 caracteres)"
                placeholderTextColor="#8B8598"
                value={nova_senha}
                onChangeText={setNovaSenha}
                secureTextEntry
                autoCapitalize="none"
              />
            </View>

            <Text style={styles.countdownLabel}>
              Reenviar código em <Text style={styles.countdownHighlight}>00:{countdown < 10 ? `0${countdown}` : countdown}</Text>
            </Text>
          </View>

          <View style={styles.footer}>
            <TouchableOpacity style={styles.confirmButton} onPress={handleConfirm} disabled={loadingVerify}>
              {loadingVerify ? (
                <ActivityIndicator color="#ffffff" />
              ) : (
                <Text style={styles.confirmButtonText}>Confirmar</Text>
              )}
            </TouchableOpacity>
          </View>
        </>
      )}
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
    alignItems: 'center',
    paddingTop: 28,
    paddingHorizontal: 34,
  },
  iconBox: {
    width: 82,
    height: 82,
    borderRadius: 24,
    backgroundColor: '#EDE7FE',
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontFamily: 'System',
    fontSize: 21,
    fontWeight: '800',
    color: '#1B1630',
    marginTop: 24,
    marginBottom: 10,
  },
  description: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '500',
    color: '#6B6676',
    textAlign: 'center',
    lineHeight: 21,
    marginBottom: 30,
  },
  emailHighlight: {
    fontWeight: '700',
    color: '#1B1630',
  },
  pinContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 26,
  },
  pinBox: {
    width: 56,
    height: 64,
    borderRadius: 15,
    backgroundColor: '#F5F3FB',
    borderWidth: 1.5,
    borderColor: '#E9E5F4',
    alignItems: 'center',
    justifyContent: 'center',
  },
  pinBoxActive: {
    backgroundColor: '#EDE7FE',
    borderColor: '#5B18E6',
  },
  pinText: {
    fontFamily: 'System',
    fontSize: 24,
    fontWeight: '800',
    color: '#C3BDD1',
  },
  pinTextActive: {
    fontFamily: 'System',
    fontSize: 24,
    fontWeight: '800',
    color: '#1B1630',
  },
  hiddenInput: {
    position: 'absolute',
    opacity: 0,
    width: 0,
    height: 0,
  },
  countdownLabel: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '600',
    color: '#8B8598',
  },
  countdownHighlight: {
    color: '#5B18E6',
    fontWeight: '800',
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
    width: '100%',
  },
  textInput: {
    flex: 1,
    fontFamily: 'System',
    fontSize: 14,
    color: '#1B1630',
    padding: 0,
  },
  footer: {
    paddingHorizontal: 22,
    paddingBottom: 30,
  },
  confirmButton: {
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
  },
  confirmButtonText: {
    fontFamily: 'System',
    fontSize: 15,
    fontWeight: '800',
    color: '#ffffff',
  },
});
