import React, { useState, useEffect, useCallback } from 'react';
import { StyleSheet, Text, View, ScrollView, TextInput, TouchableOpacity, RefreshControl, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { useRouter } from 'expo-router';
import { parcerias } from '@/services/api';

const COLORS_BG = ['#EDE7FE', '#DDF3E8', '#FBF0D9', '#FDE7E7', '#E7F0FD'];
const COLORS_TEXT = ['#5B18E6', '#159B5E', '#B57A12', '#E8433D', '#3B7DD8'];

export default function CentrosParceirosScreen() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [partners, setPartners] = useState<any[]>([]);

  useEffect(() => { loadPartners(); }, []);

  async function loadPartners() {
    try {
      setLoading(true);
      const data = await parcerias.list();
      setPartners(Array.isArray(data) ? data : data?.results || []);
    } catch (err) {
      console.error('Erro ao carregar parceiros:', err);
    } finally {
      setLoading(false);
    }
  }

  const onRefresh = useCallback(async () => {
    try {
      setRefreshing(true);
      const data = await parcerias.list({ search: search || undefined });
      setPartners(Array.isArray(data) ? data : data?.results || []);
    } catch (err) {
      console.error('Erro ao atualizar:', err);
    } finally {
      setRefreshing(false);
    }
  }, [search]);

  async function handleSearch(text: string) {
    setSearch(text);
    try {
      const data = await parcerias.list({ search: text || undefined });
      setPartners(Array.isArray(data) ? data : data?.results || []);
    } catch (err) {
      console.error('Erro na pesquisa:', err);
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />

      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <MaterialCommunityIcons name="arrow-left" size={22} color="#1B1630" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Centros Parceiros</Text>
      </View>

      <View style={styles.searchContainer}>
        <View style={styles.searchBox}>
          <MaterialCommunityIcons name="magnify" size={20} color="#9A93AD" />
          <TextInput
            style={styles.searchInput}
            placeholder="Procurar centros parceiros…"
            placeholderTextColor="#9A93AD"
            value={search}
            onChangeText={handleSearch}
          />
        </View>
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
          {partners.length > 0 ? (
            partners.map((partner, idx) => {
              const color = COLORS_TEXT[idx % COLORS_TEXT.length];
              const bg = COLORS_BG[idx % COLORS_BG.length];
              const abbr = (partner.nome_empresa || '').substring(0, 2).toUpperCase();

              return (
                <TouchableOpacity
                  key={partner.id}
                  style={styles.card}
                  activeOpacity={0.7}
                  onPress={() => {
                    if (partner.centro) {
                      router.push(`/escola/${partner.centro}`);
                    }
                  }}
                >
                  <View style={[styles.avatar, { backgroundColor: bg }]}>
                    <Text style={[styles.avatarText, { color }]}>{abbr}</Text>
                  </View>
                  <View style={styles.info}>
                    <Text style={styles.name} numberOfLines={1}>{partner.nome_empresa}</Text>
                    <Text style={styles.type}>{partner.tipo_parceria}</Text>
                    <View style={styles.metaRow}>
                      <MaterialCommunityIcons name="account-group-outline" size={13} color="#8B8598" />
                      <Text style={styles.metaText}>{partner.total_candidatos || 0} candidatos</Text>
                      {partner.localizacao ? (
                        <>
                          <MaterialCommunityIcons name="map-marker-outline" size={13} color="#8B8598" style={{ marginLeft: 8 }} />
                          <Text style={styles.metaText}>{partner.localizacao}</Text>
                        </>
                      ) : null}
                    </View>
                  </View>
                  <View style={[styles.badge, styles.badgeActive]}>
                    <Text style={[styles.badgeText, { color: '#159B5E' }]}>
                      Visitar
                    </Text>
                  </View>
                </TouchableOpacity>
              );
            })
          ) : (
            <View style={styles.emptyState}>
              <MaterialCommunityIcons name="handshake-outline" size={48} color="#D4C4FE" />
              <Text style={styles.emptyTitle}>Nenhum parceiro encontrado</Text>
              <Text style={styles.emptySub}>Quando houver centros parceiros, eles aparecerão aqui.</Text>
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
  searchContainer: { paddingHorizontal: 20, marginBottom: 10 },
  searchBox: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#ffffff', borderWidth: 1, borderColor: '#ECE8F3', borderRadius: 16, paddingHorizontal: 16, paddingVertical: 12, gap: 10 },
  searchInput: { flex: 1, fontFamily: 'System', fontSize: 14, color: '#1B1630', padding: 0 },
  listContainer: { paddingHorizontal: 20, paddingTop: 8, paddingBottom: 20, gap: 14 },
  card: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#ffffff', borderRadius: 18, borderWidth: 1, borderColor: '#ECE8F3', padding: 14, gap: 14 },
  avatar: { width: 52, height: 52, borderRadius: 14, alignItems: 'center', justifyContent: 'center' },
  avatarText: { fontFamily: 'System', fontSize: 18, fontWeight: '800' },
  info: { flex: 1 },
  name: { fontFamily: 'System', fontSize: 14, fontWeight: '700', color: '#1B1630' },
  type: { fontFamily: 'System', fontSize: 12, fontWeight: '500', color: '#8B8598', marginTop: 2 },
  metaRow: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 4 },
  metaText: { fontFamily: 'System', fontSize: 11, fontWeight: '500', color: '#8B8598' },
  badge: { paddingHorizontal: 10, paddingVertical: 5, borderRadius: 8, backgroundColor: '#F3F0FB' },
  badgeActive: { backgroundColor: '#DDF3E8' },
  badgeText: { fontFamily: 'System', fontSize: 11, fontWeight: '700', color: '#8B8598' },
  badgeTextActive: { color: '#159B5E' },
  emptyState: { alignItems: 'center', paddingTop: 60 },
  emptyTitle: { fontFamily: 'System', fontSize: 16, fontWeight: '700', color: '#1B1630', marginTop: 16 },
  emptySub: { fontFamily: 'System', fontSize: 13, fontWeight: '500', color: '#8B8598', textAlign: 'center', marginTop: 6, paddingHorizontal: 40 },
});
