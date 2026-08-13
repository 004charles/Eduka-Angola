import React, { useState } from 'react';
import { StyleSheet, Text, View, ScrollView, TextInput, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';

const ALL_COURSES = [
  {
    id: 1,
    title: 'Programação Web Completa',
    category: 'Tecnologia',
    level: 'Iniciante',
    center: 'IP Luanda',
    price: '45.000 Kz',
    bgColor: '#EDE7FE',
    tagColor: '#5B18E6',
    tagBg: '#EDE7FE',
  },
  {
    id: 2,
    title: 'Contabilidade e Finanças',
    category: 'Gestão',
    level: 'Intermédio',
    center: 'Instituto Médio de Economia',
    price: '60.000 Kz',
    bgColor: '#FBF0D9',
    tagColor: '#B57A12',
    tagBg: '#FBF0D9',
  },
  {
    id: 3,
    title: 'Inglês para Profissionais',
    category: 'Idiomas',
    level: 'Avançado',
    center: 'British Center',
    price: 'Bolsa 100%',
    bgColor: '#DDF3E8',
    tagColor: '#159B5E',
    tagBg: '#DDF3E8',
  },
];

export default function ExploreScreen() {
  const [search, setSearch] = useState('');
  const [activeTab, setActiveTab] = useState('Todos');

  const filteredCourses = ALL_COURSES.filter((course) => {
    const matchesSearch = course.title.toLowerCase().includes(search.toLowerCase()) || 
                          course.center.toLowerCase().includes(search.toLowerCase());
    const matchesTab = activeTab === 'Todos' || course.category === activeTab;
    return matchesSearch && matchesTab;
  });

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      
      {/* Header Title */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Catálogo de cursos</Text>
      </View>

      {/* Search Input Box */}
      <View style={styles.searchContainer}>
        <View style={styles.searchBox}>
          <MaterialCommunityIcons name="magnify" size={20} color="#9A93AD" />
          <TextInput
            style={styles.searchInput}
            placeholder="Procurar cursos, áreas…"
            placeholderTextColor="#9A93AD"
            value={search}
            onChangeText={setSearch}
          />
        </View>
        <TouchableOpacity style={styles.filterButton}>
          <MaterialCommunityIcons name="filter-variant" size={22} color="#5B18E6" />
        </TouchableOpacity>
      </View>

      {/* Categories Horizontal Selector */}
      <View style={{ height: 50, marginVertical: 4 }}>
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false} 
          contentContainerStyle={styles.tabContainer}
        >
          {['Todos', 'Tecnologia', 'Gestão', 'Idiomas'].map((tab) => {
            const isActive = activeTab === tab;
            return (
              <TouchableOpacity
                key={tab}
                style={[styles.tabPill, isActive ? styles.tabPillActive : null]}
                onPress={() => setActiveTab(tab)}
              >
                <Text style={[styles.tabText, isActive ? styles.tabTextActive : null]}>
                  {tab}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </View>

      {/* Courses Vertical List */}
      <ScrollView contentContainerStyle={styles.listContainer} showsVerticalScrollIndicator={false}>
        {filteredCourses.length > 0 ? (
          filteredCourses.map((course) => (
            <View key={course.id} style={styles.courseRow}>
              {/* Image box placeholder */}
              <View style={[styles.imageBox, { backgroundColor: course.bgColor }]}>
                <MaterialCommunityIcons name="school" size={26} color={course.tagColor} />
              </View>

              {/* Information body */}
              <View style={styles.infoBox}>
                <View style={styles.badgeRow}>
                  <View style={[styles.badge, { backgroundColor: course.tagBg }]}>
                    <Text style={[styles.badgeText, { color: course.tagColor }]}>
                      {course.category}
                    </Text>
                  </View>
                  <Text style={styles.levelText}>{course.level}</Text>
                </View>
                
                <Text style={styles.courseTitle} numberOfLines={2}>{course.title}</Text>
                <Text style={styles.centerName}>{course.center}</Text>

                {/* Bottom details inside item */}
                <View style={styles.cardFooter}>
                  <Text style={styles.priceText}>{course.price}</Text>
                  <TouchableOpacity style={styles.actionArrow}>
                    <MaterialCommunityIcons name="arrow-right" size={16} color="#5B18E6" />
                  </TouchableOpacity>
                </View>
              </View>
            </View>
          ))
        ) : (
          <View style={styles.emptyContainer}>
            <MaterialCommunityIcons name="alert-circle-outline" size={48} color="#9A93AD" />
            <Text style={styles.emptyText}>Nenhum curso encontrado</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F6F5FA',
  },
  header: {
    paddingHorizontal: 20,
    paddingVertical: 14,
  },
  headerTitle: {
    fontFamily: 'System',
    fontSize: 19,
    fontWeight: '800',
    color: '#1B1630',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    gap: 12,
    marginBottom: 10,
  },
  searchBox: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#ECE8F3',
    borderRadius: 16,
    paddingHorizontal: 16,
    paddingVertical: 11,
    gap: 10,
  },
  searchInput: {
    flex: 1,
    fontFamily: 'System',
    fontSize: 14,
    color: '#1B1630',
    padding: 0,
  },
  filterButton: {
    width: 48,
    height: 48,
    borderRadius: 16,
    backgroundColor: '#EDE7FE',
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabContainer: {
    paddingHorizontal: 20,
    gap: 9,
  },
  tabPill: {
    paddingHorizontal: 15,
    paddingVertical: 9,
    borderRadius: 99,
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#ECE8F3',
    height: 38,
    justifyContent: 'center',
  },
  tabPillActive: {
    backgroundColor: '#5B18E6',
    borderColor: '#5B18E6',
  },
  tabText: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '700',
    color: '#5A5567',
  },
  tabTextActive: {
    color: '#ffffff',
  },
  listContainer: {
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 20,
    gap: 14,
  },
  courseRow: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#ECE8F3',
    padding: 12,
    gap: 14,
  },
  imageBox: {
    width: 82,
    height: 82,
    borderRadius: 15,
    alignItems: 'center',
    justifyContent: 'center',
  },
  infoBox: {
    flex: 1,
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  badge: {
    paddingHorizontal: 7,
    paddingVertical: 3,
    borderRadius: 6,
  },
  badgeText: {
    fontFamily: 'System',
    fontSize: 10,
    fontWeight: '700',
  },
  levelText: {
    fontFamily: 'System',
    fontSize: 10,
    fontWeight: '600',
    color: '#8B8598',
  },
  courseTitle: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '800',
    color: '#1B1630',
    lineHeight: 18,
    marginBottom: 4,
  },
  centerName: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '500',
    color: '#8B8598',
    marginBottom: 10,
  },
  cardFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  priceText: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '800',
    color: '#1B1630',
  },
  actionArrow: {
    width: 28,
    height: 28,
    borderRadius: 8,
    backgroundColor: '#EDE7FE',
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
    gap: 12,
  },
  emptyText: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '600',
    color: '#9A93AD',
  },
});
