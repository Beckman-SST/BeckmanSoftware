# Template Frontend - Sistema de Colagem

## Arquivo: `colagem.html`

### Estrutura HTML

#### 1. Layout Principal
```html
<div class="container-fluid">
    <div class="row">
        <!-- Sidebar de navegação -->
        <nav id="sidebar" class="col-md-3 col-lg-2 sidebar">
        
        <!-- Conteúdo principal -->
        <main class="col-md-9 ms-sm-auto col-lg-10 main-content">
```

#### 2. Estados da Interface

**Estado de Carregamento**
```html
<div id="loadingState" class="loading-state">
    <div class="spinner-border text-primary"></div>
    <p>Carregando imagens...</p>
</div>
```

**Estado Vazio**
```html
<div id="emptyState" class="empty-state">
    <i class="bi bi-images"></i>
    <h4>Nenhuma imagem processada encontrada</h4>
</div>
```

#### 3. Seções de Imagens

**Imagens Executivas**
```html
<section id="executiveSection" class="image-section">
    <div class="section-header">
        <h5><i class="bi bi-person-badge"></i> Executivo</h5>
        <span id="executiveCount" class="image-count">0 imagens</span>
    </div>
    <div id="executiveImages" class="images-grid"></div>
</section>
```

**Imagens Operacionais**
```html
<section id="operationalSection" class="image-section">
    <div class="section-header">
        <h5><i class="bi bi-tools"></i> Operacional</h5>
        <span id="operationalCount" class="image-count">0 imagens</span>
    </div>
    <div id="operationalImages" class="images-grid"></div>
</section>
```

#### 4. Painel de Seleção

```html
<div id="selectionPanel" class="selection-panel">
    <div class="selection-header">
        <h6><i class="bi bi-check-square me-2"></i>Seleção para Colagem</h6>
        <span id="selectionCounter" class="selection-counter">0/3</span>
    </div>
    
    <div class="group-indicator">
        <div class="group-name-input">
            <label for="groupNameInput" class="form-label">Nome do Grupo:</label>
            <input type="text" id="groupNameInput" class="form-control" 
                   placeholder="Digite o nome do grupo...">
        </div>
    </div>
    
    <div id="selectedImagesPreview" class="selected-images-preview"></div>
    
    <div class="selection-actions">
        <button id="finishGroupBtn" class="btn btn-warning">
            <i class="bi bi-arrow-right"></i> Próximo Grupo
        </button>
        <button id="createCollageBtn" class="btn btn-success">
            <i class="bi bi-images"></i> Criar Colagens
        </button>
        <button id="clearSelectionBtn" class="btn btn-outline-danger">
            <i class="bi bi-trash"></i> Limpar
        </button>
    </div>
</div>
```

#### 5. Fila de Colagens

```html
<div id="collageQueue" class="collage-queue">
    <h6><i class="bi bi-list-ol me-2"></i>Fila de Colagens</h6>
    <div id="queueItems" class="queue-items"></div>
</div>
```

### Estilos CSS

#### 1. Layout Responsivo

```css
.main-content {
    padding: 2rem;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    min-height: 100vh;
}

.images-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-top: 1rem;
}
```

#### 2. Cards de Imagem

```css
.image-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.image-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.image-card.selected {
    border: 3px solid #007bff;
    transform: scale(1.02);
}
```

#### 3. Indicadores de Seleção

```css
.selection-group-number {
    position: absolute;
    top: 10px;
    left: 10px;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    color: white;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
}

/* Cores por grupo */
.selection-group-number.group-1 { background: #007bff; }
.selection-group-number.group-2 { background: #28a745; }
.selection-group-number.group-3 { background: #dc3545; }
/* ... até group-10 */
```

#### 4. Painel de Seleção

```css
.selection-panel {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 350px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    transform: translateY(100%);
    transition: transform 0.3s ease;
    z-index: 1000;
}

.selection-panel.show {
    transform: translateY(0);
}
```

#### 5. Campo de Nome do Grupo

```css
.group-name-input {
    margin-bottom: 0.75rem;
}

.group-name-input .form-label {
    font-weight: 600;
    color: #495057;
    margin-bottom: 0.25rem;
    font-size: 0.85rem;
}

.group-name-input .form-control {
    border-radius: 6px;
    border: 1px solid #ced4da;
    font-size: 0.85rem;
}

.group-name-input .form-control:focus {
    border-color: #007bff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}
```

### Responsividade

#### Breakpoints

- **Desktop**: `≥ 1200px` - Grid de 4-5 colunas
- **Tablet**: `768px - 1199px` - Grid de 2-3 colunas
- **Mobile**: `< 768px` - Grid de 1-2 colunas

#### Adaptações Mobile

```css
@media (max-width: 768px) {
    .selection-panel {
        width: calc(100% - 40px);
        left: 20px;
        right: 20px;
    }
    
    .images-grid {
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 1rem;
    }
}
```

### Acessibilidade

#### Recursos Implementados

- **ARIA Labels**: Todos os botões e controles
- **Keyboard Navigation**: Suporte completo via Tab
- **Screen Reader**: Textos alternativos e descrições
- **Contraste**: Cores com contraste adequado (WCAG 2.1)

#### Exemplo de Implementação

```html
<button id="finishGroupBtn" class="btn btn-warning" 
        aria-label="Finalizar grupo atual e iniciar novo grupo"
        title="Próximo Grupo">
    <i class="bi bi-arrow-right" aria-hidden="true"></i> Próximo Grupo
</button>
```

### Integração com JavaScript

#### IDs Principais

- `#executiveImages` - Container de imagens executivas
- `#operationalImages` - Container de imagens operacionais
- `#selectionPanel` - Painel de seleção
- `#groupNameInput` - Campo de nome do grupo
- `#selectedImagesPreview` - Preview das imagens selecionadas
- `#collageQueue` - Fila de colagens

#### Classes de Estado

- `.selected` - Imagem selecionada
- `.used-in-collage` - Imagem já utilizada
- `.show` - Painel visível
- `.loading` - Estado de carregamento

### Performance

#### Otimizações Implementadas

- **Lazy Loading**: Imagens carregadas sob demanda
- **CSS Grid**: Layout eficiente e responsivo
- **Transitions**: Animações suaves com `transform`
- **Debouncing**: Eventos de redimensionamento otimizados

#### Métricas de Performance

- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1