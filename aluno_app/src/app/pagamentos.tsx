import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, StatusBar, RefreshControl } from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { pagamentos } from '@/services/api';

const COLORS = {
  purple: '#5B18E6',
  dark: '#1B1630',
  gray: '#8B8598',
  bg: '#F6F5FA',
  border: '#ECE8F3',
  lightPurple: '#EDE7FE',
};

interface Payment {
  id: string;
  curso_nome?: string;
  curso?: { nome?: string };
  valor: number;
  moeda?: string;
  forma_pagamento?: string;
  status?: string;
  data_criacao?: string;
  referencia_pagamento?: string;
}

const STATUS_MAP: Record<string, { color: string; bg: string; label: string }> = {
  processado: { color: '#22C55E', bg: '#DCFCE7', label: 'Processado' },
  pendente: { color: '#F59E0B', bg: '#FEF3C7', label: 'Pendente' },
  recusado: { color: '#EF4444', bg: '#FEE2E2', label: 'Recusado' },
  cancelado: { color: '#6B7280', bg: '#F3F4F6', label: 'Cancelado' },
};

function formatDate(dateStr?: string) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('pt-AO', { day: '2-digit', month: 'short', year: 'numeric' });
}

function formatMoney(value: number) {
  return value.toLocaleString('pt-AO') + ' Kz';
}

export default function PagamentosScreen() {
  const router = useRouter();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchPayments = useCallback(async () => {
    try {
      const data = await pagamentos.list();
      const items = Array.isArray(data) ? data : data?.results || [];
      setPayments(items);
    } catch {
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchPayments();
  }, [fetchPayments]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchPayments();
  }, [fetchPayments]);

  const totalInvested = payments.reduce((sum, p) => sum + (p.valor || 0), 0);

  const getCourseName = (p: Payment) => p.curso_nome || p.curso?.nome || 'Curso';

  const getMethodName = (p: Payment) => {
    const map: Record<string, string> = {
      transferencia: 'Transferência',
      multicaixa: 'Multicaixa',
      visa: 'Visa',
    };
    return map[p.forma_pagamento || ''] || p.forma_pagamento || '';
  };

  const getStatus = (p: Payment) => STATUS_MAP[p.status?.toLowerCase() || 'pendente'] || STATUS_MAP.pendente;

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.bg} />
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color={COLORS.dark} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Pagamentos</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.purple} />}
      >
        {/* Total Invested Card */}
        <View style={styles.totalCard}>
          <View style={styles.totalCardInner}>
            <MaterialCommunityIcons name="chart-line-variant" size={28} color="#fff" />
            <Text style={styles.totalLabel}>Total investido em formação</Text>
            <Text style={styles.totalAmount}>{formatMoney(totalInvested)}</Text>
          </View>
        </View>

        {/* Loading */}
        {loading && (
          <Text style={{ textAlign: 'center', color: COLORS.gray, marginTop: 32 }}>A carregar pagamentos...</Text>
        )}

        {/* Payment Cards */}
        {!loading && payments.map((payment) => {
          const status = getStatus(payment);
          return (
            <View key={payment.id} style={styles.paymentCard}>
              <View style={styles.paymentRow}>
                <View style={styles.paymentIconWrap}>
                  <MaterialCommunityIcons name="receipt" size={22} color={COLORS.purple} />
                </View>
                <View style={styles.paymentInfo}>
                  <Text style={styles.paymentCourse}>{getCourseName(payment)}</Text>
                  <Text style={styles.paymentMeta}>
                    {getMethodName(payment)}{payment.data_criacao ? ` · ${formatDate(payment.data_criacao)}` : ''}
                  </Text>
                </View>
                <Text style={styles.paymentAmount}>{formatMoney(payment.valor)}</Text>
              </View>
              <View style={[styles.statusBadge, { backgroundColor: status.bg }]}>
                <View style={[styles.statusDot, { backgroundColor: status.color }]} />
                <Text style={[styles.statusText, { color: status.color }]}>{status.label}</Text>
              </View>
            </View>
          );
        })}

        {!loading && payments.length === 0 && (
          <Text style={{ textAlign: 'center', color: COLORS.gray, marginTop: 32 }}>Nenhum pagamento encontrado.</Text>
        )}

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
  totalCard: {
    borderRadius: 18,
    overflow: 'hidden',
    marginBottom: 24,
    shadowColor: COLORS.purple,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  totalCardInner: {
    backgroundColor: COLORS.purple,
    padding: 24,
    borderRadius: 18,
  },
  totalLabel: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
    fontFamily: 'System',
    marginTop: 12,
    marginBottom: 4,
  },
  totalAmount: {
    fontSize: 32,
    fontWeight: '800',
    color: '#fff',
    fontFamily: 'System',
  },
  paymentCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 12,
  },
  paymentRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  paymentIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: COLORS.lightPurple,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  paymentInfo: {
    flex: 1,
  },
  paymentCourse: {
    fontSize: 15,
    fontWeight: '600',
    color: COLORS.dark,
    fontFamily: 'System',
    marginBottom: 2,
  },
  paymentMeta: {
    fontSize: 13,
    color: COLORS.gray,
    fontFamily: 'System',
  },
  paymentAmount: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.dark,
    fontFamily: 'System',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 6,
    gap: 6,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  statusText: {
    fontSize: 13,
    fontWeight: '600',
    fontFamily: 'System',
  },
});
