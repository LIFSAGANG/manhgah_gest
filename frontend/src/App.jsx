import { useState, useEffect } from 'react'
import './App.css'
import { fetchProduits, fetchCategories, fetchSocietes, fetchMouvements, addProduit } from './api'

function App() {
  const [currentPage, setCurrentPage] = useState('accueil')
  const [produits, setProduits] = useState([])
  const [categories, setCategories] = useState([])
  const [societes, setSocietes] = useState([])
  const [mouvements, setMouvements] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    setLoading(true)
    try {
      const [p, c, s, m] = await Promise.all([
        fetchProduits(),
        fetchCategories(),
        fetchSocietes(),
        fetchMouvements(),
      ])
      setProduits(p?.results || p || [])
      setCategories(c?.results || c || [])
      setSocietes(s?.results || s || [])
      setMouvements(m?.results || m || [])
    } catch (error) {
      console.error('Erreur chargement données:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <Topbar />
      <div className="app-main">
        <Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} />
        <div className="app-content">
          {currentPage === 'accueil' && <Accueil produits={produits} categories={categories} mouvements={mouvements} />}
          {currentPage === 'produits' && <Produits produits={produits} societes={societes} categories={categories} onRefresh={loadData} />}
          {currentPage === 'categories' && <Categories categories={categories} societes={societes} onRefresh={loadData} />}
          {currentPage === 'mouvements' && <Mouvements mouvements={mouvements} produits={produits} onRefresh={loadData} />}
          {currentPage === 'societes' && <Societes societes={societes} onRefresh={loadData} />}
        </div>
      </div>
    </div>
  )
}

function Topbar() {
  return (
    <div className="topbar">
      <div className="topbar-left">
        <h1>🏢 Manhgah Gest</h1>
      </div>
      <div className="topbar-right">
        <a href="/logout" className="btn-logout">Déconnexion</a>
      </div>
    </div>
  )
}

function Sidebar({ currentPage, setCurrentPage }) {
  const menuItems = [
    { id: 'accueil', label: '🏠 Accueil' },
    { id: 'produits', label: '📦 Produits' },
    { id: 'categories', label: '🏷️ Catégories' },
    { id: 'mouvements', label: '📊 Mouvements' },
    { id: 'societes', label: '🏢 Sociétés' },
  ]

  return (
    <aside className="sidebar">
      {menuItems.map((item) => (
        <button
          key={item.id}
          className={`sidebar-item ${currentPage === item.id ? 'active' : ''}`}
          onClick={() => setCurrentPage(item.id)}
        >
          {item.label}
        </button>
      ))}
    </aside>
  )
}

function Accueil({ produits, categories, mouvements }) {
  return (
    <div className="page">
      <div className="hero">
        <h2>Bienvenue dans Manhgah Gest</h2>
        <p>Application de gestion commerciale et comptable</p>
        <p className="subtitle">Gérez vos produits, catégories, stocks et mouvements en un seul endroit</p>
      </div>
      <div className="cards">
        <Card title="📦 Produits" count={produits.length} />
        <Card title="🏷️ Catégories" count={categories.length} />
        <Card title="📊 Mouvements" count={mouvements.length} />
      </div>
    </div>
  )
}

function Card({ title, count }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <p className="count">{count}</p>
    </div>
  )
}

function Produits({ produits, societes, categories, onRefresh }) {
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    reference: '',
    nom: '',
    prix_unitaire: '',
    date_creation: '',
    societe: societes.length > 0 ? societes[0].id : '',
    categorie: categories.length > 0 ? categories[0].id : '',
  })
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await addProduit(form)
      alert('Produit enregistré ✓')
      setForm({ reference: '', nom: '', prix_unitaire: '', date_creation: '', societe: societes[0]?.id || '', categorie: categories[0]?.id || '' })
      setShowForm(false)
      onRefresh()
    } catch (error) {
      alert('Erreur: ' + error.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h2>📦 Produits ({produits.length})</h2>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Fermer' : '+ Ajouter'}
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>Société *</label>
                <select
                  value={form.societe}
                  onChange={(e) => setForm({ ...form, societe: e.target.value })}
                  required
                >
                  <option value="">-- Sélectionner --</option>
                  {societes.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.nom}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Référence *</label>
                <input
                  type="text"
                  placeholder="REF-001"
                  value={form.reference}
                  onChange={(e) => setForm({ ...form, reference: e.target.value })}
                  required
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Nom *</label>
                <input
                  type="text"
                  placeholder="Nom du produit"
                  value={form.nom}
                  onChange={(e) => setForm({ ...form, nom: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Catégorie</label>
                <select
                  value={form.categorie}
                  onChange={(e) => setForm({ ...form, categorie: e.target.value })}
                >
                  <option value="">-- Sélectionner --</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.nom}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Prix unitaire *</label>
                <input
                  type="number"
                  placeholder="0.00"
                  step="0.01"
                  value={form.prix_unitaire}
                  onChange={(e) => setForm({ ...form, prix_unitaire: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Date création *</label>
                <input
                  type="date"
                  value={form.date_creation}
                  onChange={(e) => setForm({ ...form, date_creation: e.target.value })}
                  required
                />
              </div>
            </div>
            <button type="submit" className="btn-success" disabled={submitting}>
              {submitting ? 'Enregistrement...' : 'Enregistrer'}
            </button>
          </form>
        </div>
      )}

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Référence</th>
              <th>Nom</th>
              <th>Prix</th>
              <th>Catégorie</th>
              <th>Société</th>
              <th>Stock</th>
            </tr>
          </thead>
          <tbody>
            {produits.length === 0 ? (
              <tr>
                <td colSpan="6" className="empty">Aucun produit</td>
              </tr>
            ) : (
              produits.map((p) => (
                <tr key={p.id}>
                  <td>{p.reference}</td>
                  <td>{p.nom}</td>
                  <td>{p.prix_unitaire}</td>
                  <td>{p.categorie_nom || '-'}</td>
                  <td>{p.societe_nom || '-'}</td>
                  <td>{p.quantite_stock}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function Categories({ categories, societes, onRefresh }) {
  return (
    <div className="page">
      <div className="page-header">
        <h2>🏷️ Catégories ({categories.length})</h2>
        <button className="btn-primary">+ Ajouter</button>
      </div>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Nom</th>
              <th>Société</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {categories.length === 0 ? (
              <tr>
                <td colSpan="4" className="empty">Aucune catégorie</td>
              </tr>
            ) : (
              categories.map((c) => (
                <tr key={c.id}>
                  <td>{c.code}</td>
                  <td>{c.nom}</td>
                  <td>{c.societe_nom || '-'}</td>
                  <td>{c.description || '-'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function Mouvements({ mouvements, produits, onRefresh }) {
  return (
    <div className="page">
      <div className="page-header">
        <h2>📊 Mouvements Stock ({mouvements.length})</h2>
        <button className="btn-primary">+ Ajouter</button>
      </div>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Produit</th>
              <th>Type</th>
              <th>Quantité</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {mouvements.length === 0 ? (
              <tr>
                <td colSpan="4" className="empty">Aucun mouvement</td>
              </tr>
            ) : (
              mouvements.map((m) => (
                <tr key={m.id}>
                  <td>{m.produit_nom || '-'}</td>
                  <td>{m.type_mouvement}</td>
                  <td>{m.quantite}</td>
                  <td>{m.created_at?.split('T')[0] || '-'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function Societes({ societes, onRefresh }) {
  return (
    <div className="page">
      <div className="page-header">
        <h2>🏢 Sociétés ({societes.length})</h2>
        <button className="btn-primary">+ Ajouter</button>
      </div>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Nom</th>
              <th>Ville</th>
              <th>Téléphone</th>
              <th>Email</th>
            </tr>
          </thead>
          <tbody>
            {societes.length === 0 ? (
              <tr>
                <td colSpan="5" className="empty">Aucune société</td>
              </tr>
            ) : (
              societes.map((s) => (
                <tr key={s.id}>
                  <td>{s.code}</td>
                  <td>{s.nom}</td>
                  <td>{s.ville || '-'}</td>
                  <td>{s.telephone || '-'}</td>
                  <td>{s.email || '-'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default App
