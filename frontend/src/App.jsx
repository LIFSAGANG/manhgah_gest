import { useState, useEffect } from 'react'
import './App.css'
import {
  fetchProduits,
  fetchCategories,
  fetchSocietes,
  fetchAgences,
  fetchMouvements,
  addProduit,
  addCategorie,
  addMouvement,
} from './api'

function App() {
  const [currentPage, setCurrentPage] = useState('accueil')
  const [produits, setProduits] = useState([])
  const [categories, setCategories] = useState([])
  const [societes, setSocietes] = useState([])
  const [agences, setAgences] = useState([])
  const [mouvements, setMouvements] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    setLoading(true)
    try {
      const [p, c, s, a, m] = await Promise.all([
        fetchProduits(),
        fetchCategories(),
        fetchSocietes(),
        fetchAgences(),
        fetchMouvements(),
      ])
      setProduits(p?.results || p || [])
      setCategories(c?.results || c || [])
      setSocietes(s?.results || s || [])
      setAgences(a?.results || a || [])
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
          {currentPage === 'mouvements' && <Mouvements mouvements={mouvements} produits={produits} agences={agences} onRefresh={loadData} />}
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
    code_produit: '',
    nom_produit: '',
    prix_vente_ht: '',
    type_produit: 'Bien',
    unite_mesure: 'Unité',
    societe: societes.length > 0 ? societes[0].id : '',
    categorie: categories.length > 0 ? categories[0].id : '',
  })
  const [submitting, setSubmitting] = useState(false)

  const findSocieteNom = (societeId) => {
    const societe = societes.find((s) => String(s.id) === String(societeId))
    return societe?.raison_sociale || societe?.nom || '-'
  }

  const findCategorieNom = (categorieId) => {
    const categorie = categories.find((c) => String(c.id) === String(categorieId))
    return categorie?.nom_categorie || categorie?.nom || '-'
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await addProduit({
        ...form,
        societe: form.societe ? Number(form.societe) : null,
        categorie: form.categorie ? Number(form.categorie) : null,
        prix_vente_ht: form.prix_vente_ht ? Number(form.prix_vente_ht) : 0,
      })
      alert('Produit enregistré ✓')
      setForm({
        code_produit: '',
        nom_produit: '',
        prix_vente_ht: '',
        type_produit: 'Bien',
        unite_mesure: 'Unité',
        societe: societes[0]?.id || '',
        categorie: categories[0]?.id || '',
      })
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
                  placeholder="PROD-001"
                  value={form.code_produit}
                  onChange={(e) => setForm({ ...form, code_produit: e.target.value })}
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
                  value={form.nom_produit}
                  onChange={(e) => setForm({ ...form, nom_produit: e.target.value })}
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
                      {c.nom_categorie || c.nom}
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
                  value={form.prix_vente_ht}
                  onChange={(e) => setForm({ ...form, prix_vente_ht: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Type produit</label>
                <select value={form.type_produit} onChange={(e) => setForm({ ...form, type_produit: e.target.value })}>
                  <option value="Bien">Bien</option>
                  <option value="Service">Service</option>
                  <option value="Consommable">Consommable</option>
                </select>
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
                  <td>{p.code_produit || p.reference || '-'}</td>
                  <td>{p.nom_produit || p.nom || '-'}</td>
                  <td>{p.prix_vente_ht ?? p.prix_unitaire ?? '-'}</td>
                  <td>{findCategorieNom(p.categorie)}</td>
                  <td>{findSocieteNom(p.societe)}</td>
                  <td>{p.stock_alerte ?? p.quantite_stock ?? 0}</td>
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
  const [showForm, setShowForm] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [form, setForm] = useState({
    code_categorie: '',
    nom_categorie: '',
    societe: societes[0]?.id || '',
    description: '',
  })

  const findSocieteNom = (societeId) => {
    const societe = societes.find((s) => String(s.id) === String(societeId))
    return societe?.raison_sociale || societe?.nom || '-'
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await addCategorie({
        ...form,
        societe: form.societe ? Number(form.societe) : null,
      })
      alert('Catégorie enregistrée ✓')
      setForm({ code_categorie: '', nom_categorie: '', societe: societes[0]?.id || '', description: '' })
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
        <h2>🏷️ Catégories ({categories.length})</h2>
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
                      {s.raison_sociale || s.nom}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Code catégorie *</label>
                <input
                  type="text"
                  value={form.code_categorie}
                  onChange={(e) => setForm({ ...form, code_categorie: e.target.value })}
                  required
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Nom catégorie *</label>
                <input
                  type="text"
                  value={form.nom_categorie}
                  onChange={(e) => setForm({ ...form, nom_categorie: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <input
                  type="text"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
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
                  <td>{c.code_categorie || c.code || '-'}</td>
                  <td>{c.nom_categorie || c.nom || '-'}</td>
                  <td>{findSocieteNom(c.societe)}</td>
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

function Mouvements({ mouvements, produits, agences, onRefresh }) {
  const [showForm, setShowForm] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [form, setForm] = useState({
    produit: produits[0]?.id || '',
    agence: '',
    type_mouvement: 'entree',
    quantite: '',
    prix_unitaire: '',
    agence_destination: '',
    reference: '',
    motif: '',
  })

  const findProduitNom = (produitId) => {
    const produit = produits.find((p) => String(p.id) === String(produitId))
    return produit?.nom_produit || produit?.nom || '-'
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await addMouvement({
        ...form,
        produit: form.produit ? Number(form.produit) : null,
        agence: form.agence ? Number(form.agence) : null,
        agence_destination: form.agence_destination ? Number(form.agence_destination) : null,
        quantite: form.quantite ? Number(form.quantite) : 0,
        prix_unitaire: form.prix_unitaire ? Number(form.prix_unitaire) : null,
      })
      alert('Mouvement enregistré ✓')
      setForm({
        produit: produits[0]?.id || '',
        agence: '',
        type_mouvement: 'entree',
        quantite: '',
        prix_unitaire: '',
        agence_destination: '',
        reference: '',
        motif: '',
      })
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
        <h2>📊 Mouvements Stock ({mouvements.length})</h2>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Fermer' : '+ Ajouter'}
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>Produit *</label>
                <select value={form.produit} onChange={(e) => setForm({ ...form, produit: e.target.value })} required>
                  <option value="">-- Sélectionner --</option>
                  {produits.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.nom_produit || p.nom}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Agence source *</label>
                <select value={form.agence} onChange={(e) => setForm({ ...form, agence: e.target.value })} required>
                  <option value="">-- Sélectionner --</option>
                  {agences.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.nom}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Type mouvement *</label>
                <select value={form.type_mouvement} onChange={(e) => setForm({ ...form, type_mouvement: e.target.value })} required>
                  <option value="entree">Entrée</option>
                  <option value="sortie">Sortie</option>
                  <option value="transfert">Transfert</option>
                  <option value="ajustement">Ajustement</option>
                  <option value="inventaire">Inventaire</option>
                </select>
              </div>
              <div className="form-group">
                <label>Quantité *</label>
                <input type="number" value={form.quantite} onChange={(e) => setForm({ ...form, quantite: e.target.value })} required />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Prix unitaire</label>
                <input type="number" step="0.01" value={form.prix_unitaire} onChange={(e) => setForm({ ...form, prix_unitaire: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Agence destination</label>
                <select value={form.agence_destination} onChange={(e) => setForm({ ...form, agence_destination: e.target.value })}>
                  <option value="">-- Aucune --</option>
                  {agences.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.nom}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Référence</label>
                <input type="text" value={form.reference} onChange={(e) => setForm({ ...form, reference: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Motif</label>
                <input type="text" value={form.motif} onChange={(e) => setForm({ ...form, motif: e.target.value })} />
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
                  <td>{findProduitNom(m.produit)}</td>
                  <td>{m.type_mouvement}</td>
                  <td>{m.quantite}</td>
                  <td>{(m.date_mouvement || m.created_at || '').split('T')[0] || '-'}</td>
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
                  <td>{s.code_societe || s.code || '-'}</td>
                  <td>{s.raison_sociale || s.nom || '-'}</td>
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
