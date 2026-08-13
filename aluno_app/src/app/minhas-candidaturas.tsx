import React, { useState, useEffect, useCallback } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, RefreshControl, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { useRouter } from 'expo-router';
import { candidaturas } from '@/services/api';

const STATUS_CONFIG: Record<string, { color: string; bg: string; icon: string; label: string }> = {
  P: { color: '#B57A12', bg: '#FBF0D9', icon: 'clock-outline', label: 'Pendente' },
  A: { color: '#159B5E', bg: '#DDF3E8', icon: 'check-circle', label: 'Aprovada' },
  R: { color: '#E8433D', bg: '#FDE7E7', icon: 'close-circle', label: 'Rejeitada' },
  C: { color: '#8B8598', bg: '#F3F0FB', icon: 'cancel', label: 'Cancelada' },
};

export default function MinhasCandidaturasScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => { loadCandidaturas(); }, []);

  async function loadCandidaturas() {
    try {
      setLoading(true);
      const data = await candidaturas.list();
      setItems(Array.isArray(data) ? data : data?.results || []);
    } catch (err) {
      console.error('Erro ao carregar candidaturas:', err);
    } finally {
      setLoading(false);
    }
  }

  const onRefresh = useCallback(async () => {
    try {
      setRefreshing(true);
      const data = await candidaturas.list();
      setItems(Array.isArray(data) ? data : data?.results || []);
    } catch (err) {
      console.error('Erro ao atualizar:', err);
    } finally {
      setRefreshing(false);
    }
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <MaterialCommunityIcons name="arrow-left" size={22} color="#1B1630" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Minhas Candidaturas</Text>
      </View>

      {loading ? (
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
          <ActivityIndicator size="large" color="#5B18E6" />
        </View>
      ) : (
        <ScrollView
          contentContainerStyle={styles.listContainer}
          showsVerticalScrollIndicator={false}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#5B18E6" />}
        >
          {items.length > 0 ? (
            items.map((item) => {
              const st = STATUS_CONFIG[item.status] || STATUS_CONFIG.P;
              return (
                <View key={item.id} style={styles.card}>
                  <View style={styles.cardHeader}>
                    <View style={styles.cardTitleRow}>
                      <Text style={styles.courseName} numberOfLines={1}>{item.curso_nome}</Text>
                    </View>
                    <View style={[styles.statusBadge, { backgroundColor: st.bg }]}>
                      <MaterialCommunityIcons name={st.icon as any} size={14} color={st.color} />
                      <Text style={[styles.statusText, { color: st.color }]}>{st.label}</Text>
                    </View>
                  </View>

                  <View style={styles.partnerRow}>
                    <MaterialCommunityIcons name="domain" size={14} color="#8B8598" />
                    <Text style={styles.partnerName}>{item.parceria_nome}</Text>
                  </View>

                  <View style={styles.dateRow}>
                    <MaterialCommunityIcons name="calendar-outline" size={13} color="#8B8598" />
                    <Text style={styles.dateText}>
                      Submetida em {new Date(item.data_criacao).toLocaleDateString('pt-AO')}
                    </Text>
                  </View>

                  {item.resposta_admin ? (
                    <View style={styles.responseBox}>
                      <Text style={styles.responseLabel}>Resposta do centro:</Text>
                      <Text style={styles.responseText}>{item.resposta_admin}</Text>
                    </View>
                  ) : null}
                </View>
              );
            })
          ) : (
            <View style={styles.emptyState}>
              <MaterialCommunityIcons name="file-document-outline" size={48} color="#D4C4FE" />
              <Text style={styles.emptyTitle}>Nenhuma candidatura</Text>
              <Text style={styles.emptySub}>Submeta a sua primeira candidatura a um centro parceiro.</Text>
              <TouchableOpacity style={styles.emptyBtn} onPress={() => router.push('/centros-parceiros')}>
                <Text style={styles.emptyBtnText}>Explorar parceiros</Text>
              </TouchableOpacity>
            </View>
          )}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F6F5FA' },
  header: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 20, paddingVertical: 14, gap: 12 },
  backBtn: { width: 40, height: 40, borderRadius: 12, backgroundColor: '#ffffff', borderWidth: 1, borderColor: '#ECE8F3', alignItems: 'center', justifyContent: 'center' },
  headerTitle: { fontFamily: 'System', fontSize: 19, fontWeight: '800', color: '#1B1630' },
  listContainer: { paddingHorizontal: 20, paddingTop: 8, paddingBottom: 20, gap: 14 },
  card: { backgroundColor: '#ffffff', borderRadius: 18, borderWidth: 1, borderColor: '#ECE8F3', padding: 16 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10 },
  cardTitleRow: { flex: 1 },
  courseName: { fontFamily: 'System', fontSize: 15, fontWeight: '800', color: '#1B1630' },
  statusBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 10, paddingVertical: 5, borderRadius: 8 },
  statusText: { fontFamily: 'System', fontSize: 11, fontWeight: '700' },
  partnerRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 8 },
  partnerName: { fontFamily: 'System', fontSize: 12, fontWeight: '600', color: '#8B8598' },
  dateRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 6 },
  dateText: { fontFamily: 'System', fontSize: 11, fontWeight: '500', color: '#8B8598' },
  responseBox: { backgroundColor: '#F5F3FB', borderRadius: 12, padding: 12, marginTop: 10 },
  responseLabel: { fontFamily: 'System', fontSize: 11, fontWeight: '700', color: '#4A4557', marginBottom: 4 },
  responseText: { fontFamily: 'System', fontSize: 12, fontWeight: '500', color: '#4A4557', lineHeight: 18 },
  emptyState: { alignItems: 'center', paddingTop: 60 },
  emptyTitle: { fontFamily: 'System', fontSize: 16, fontWeight: '700', color: '#1B1630', marginTop: 16 },
  emptySub: { fontFamily: 'System', fontSize: 13, fontWeight: '500', color: '#8B8598', textAlign: 'center', marginTop: 6, paddingHorizontal: 40 },
  emptyBtn: { backgroundColor: '#5B18E6', borderRadius: 12, paddingHorizontal: 24, paddingVertical: 12, marginTop: 20 },
  emptyBtnText: { fontFamily: 'System', fontSize: 13, fontWeight: '700', color: '#ffffff' },
});
