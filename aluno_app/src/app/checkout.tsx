import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, StatusBar, Alert } from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { pagamentos } from '@/services/api';

const COLORS = {
  purple: '#5B18E6',
  dark: '#1B1630',
  gray: '#8B8598',
  bg: '#F6F5FA',
  border: '#ECE8F3',
  lightPurple: '#EDE7FE',
};

export default function CheckoutScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{
    cursoId?: string;
    cursoNome?: string;
    instituicao?: string;
    preco?: string;
  }>();

  const [paymentMethod, setPaymentMethod] = useState('transferencia');
  const [loading, setLoading] = useState(false);

  const cursoId = params.cursoId ? Number(params.cursoId) : undefined;
  const cursoNome = params.cursoNome || 'Introdução à Programação Web';
  const instituicao = params.instituicao || 'Instituto Politécnico de Luanda';
  const preco = params.preco || '45.000 Kz';
  const precoNumerico = params.preco ? Number(params.preco.replace(/\D/g, '')) : 45000;

  const paymentOptions = [
    { id: 'transferencia', label: 'Transferência bancária' },
    { id: 'multicaixa', label: 'Multicaixa Express' },
    { id: 'visa', label: 'Cartão Visa' },
  ];

  const handleConfirm = async () => {
    if (!cursoId) {
      Alert.alert('Erro', 'Curso não identificado.');
      return;
    }
    setLoading(true);
    try {
      await pagamentos.criar({
        curso_id: cursoId,
        valor: precoNumerico,
        moeda: 'AOA',
        forma_pagamento: paymentMethod,
      });
      Alert.alert('Sucesso', 'Inscrição confirmada! Redirecionando...', [
        { text: 'OK', onPress: () => router.replace('/(tabs)/home') },
      ]);
    } catch (err: any) {
      Alert.alert('Erro', err.message || 'Não foi possível processar o pagamento.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.bg} />
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color={COLORS.dark} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Finalizar inscrição</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Course Summary */}
        <View style={styles.courseCard}>
          <View style={styles.courseIconWrap}>
            <MaterialCommunityIcons name="code-tags" size={28} color={COLORS.purple} />
          </View>
          <View style={styles.courseInfo}>
            <Text style={styles.courseName}>{cursoNome}</Text>
            <Text style={styles.courseInstitution}>{instituicao}</Text>
          </View>
          <Text style={styles.coursePrice}>{preco}</Text>
        </View>

        {/* Payment Method */}
        <Text style={styles.sectionTitle}>Forma de pagamento</Text>
        <View style={styles.paymentOptions}>
          {paymentOptions.map((option) => {
            const isSelected = paymentMethod === option.id;
            return (
              <TouchableOpacity
                key={option.id}
                style={[
                  styles.paymentOption,
                  isSelected && styles.paymentOptionSelected,
                ]}
                onPress={() => setPaymentMethod(option.id)}
                activeOpacity={0.7}
              >
                <View style={[styles.radio, isSelected && styles.radioSelected]}>
                  {isSelected && <View style={styles.radioDot} />}
                </View>
                <Text style={[styles.paymentLabel, isSelected && styles.paymentLabelSelected]}>
                  {option.label}
                </Text>
                {isSelected && (
                  <MaterialCommunityIcons name="check-circle" size={20} color={COLORS.purple} />
                )}
              </TouchableOpacity>
            );
          })}
        </View>

        {/* Summary */}
        <View style={styles.summaryCard}>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Subtotal</Text>
            <Text style={styles.summaryValue}>{preco}</Text>
          </View>
          <View style={styles.summaryDivider} />
          <View style={styles.summaryRow}>
            <Text style={styles.summaryTotalLabel}>Total</Text>
            <Text style={styles.summaryTotalValue}>{preco}</Text>
          </View>
        </View>

        {/* Confirm Button */}
        <TouchableOpacity
          style={[styles.confirmBtn, loading && { opacity: 0.6 }]}
          activeOpacity={0.8}
          onPress={handleConfirm}
          disabled={loading}
        >
          <Text style={styles.confirmBtnText}>
            {loading ? 'Processando...' : 'Confirmar inscrição'}
          </Text>
        </TouchableOpacity>

        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bg,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: COLORS.bg,
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: COLORS.dark,
    fontFamily: 'System',
  },
  scrollView: {
    flex: 1,
    paddingHorizontal: 20,
  },
  courseCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 24,
  },
  courseIconWrap: {
    width: 48,
    height: 48,
    borderRadius: 12,
    backgroundColor: COLORS.lightPurple,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  courseInfo: {
    flex: 1,
  },
  courseName: {
    fontSize: 15,
    fontWeight: '600',
    color: COLORS.dark,
    fontFamily: 'System',
    marginBottom: 2,
  },
  courseInstitution: {
    fontSize: 13,
    color: COLORS.gray,
    fontFamily: 'System',
  },
  coursePrice: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.purple,
    fontFamily: 'System',
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: COLORS.gray,
    fontFamily: 'System',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 12,
  },
  paymentOptions: {
    gap: 10,
    marginBottom: 28,
  },
  paymentOption: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 16,
    borderWidth: 1.5,
    borderColor: COLORS.border,
  },
  paymentOptionSelected: {
    borderColor: COLORS.purple,
    backgroundColor: COLORS.lightPurple,
  },
  radio: {
    width: 22,
    height: 22,
    borderRadius: 11,
    borderWidth: 2,
    borderColor: COLORS.border,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  radioSelected: {
    borderColor: COLORS.purple,
  },
  radioDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: COLORS.purple,
  },
  paymentLabel: {
    flex: 1,
    fontSize: 15,
    fontWeight: '500',
    color: COLORS.dark,
    fontFamily: 'System',
  },
  paymentLabelSelected: {
    fontWeight: '600',
    color: COLORS.purple,
  },
  summaryCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 24,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 4,
  },
  summaryLabel: {
    fontSize: 15,
    color: COLORS.gray,
    fontFamily: 'System',
  },
  summaryValue: {
    fontSize: 15,
    color: COLORS.dark,
    fontWeight: '500',
    fontFamily: 'System',
  },
  summaryDivider: {
    height: 1,
    backgroundColor: COLORS.border,
    marginVertical: 12,
  },
  summaryTotalLabel: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.dark,
    fontFamily: 'System',
  },
  summaryTotalValue: {
    fontSize: 18,
    fontWeight: '700',
    color: COLORS.purple,
    fontFamily: 'System',
  },
  confirmBtn: {
    backgroundColor: COLORS.purple,
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: 'center',
    shadowColor: COLORS.purple,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  confirmBtnText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
    fontFamily: 'System',
  },
});
