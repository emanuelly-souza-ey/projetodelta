import { useEffect, useState } from "react";
import "../App.css";
import AutocompleteList from "../components/autocomplete/AutocompleteList";
import ChatBubble from "../components/chat/ChatBubble";
import ChatHeader from "../components/chat/ChatHeader";
import ChatInput from "../components/chat/ChatInput";
import EmptyState from "../components/chat/EmptyState";
import QuickReplies from "../components/chat/QuickReplies";
import TypingIndicator from "../components/chat/TypingIndicator";

const Storybook = () => {
    const [cssVariables, setCssVariables] = useState<{ [key: string]: string }>({});

    useEffect(() => {
        // Extraer todas las variables CSS del :root
        const root = document.documentElement;
        const styles = getComputedStyle(root);

        const variables: { [key: string]: string } = {};

        // Lista completa de variables CSS a extraer
        const varNames = [
            // Colores
            '--color-primary', '--color-secondary', '--color-success', '--color-warning', '--color-error', '--color-info',
            '--color-text-primary', '--color-text-secondary', '--color-text-muted',
            '--color-background', '--color-background-light', '--color-background-dark',
            '--color-border', '--color-border-light', '--color-border-dark', '--color-chat-bubble', '--color-hover',
            // Tipografía
            '--font-family-primary', '--font-family-mono',
            '--font-size-xs', '--font-size-sm', '--font-size-base', '--font-size-md', '--font-size-lg', '--font-size-xl',
            '--font-size-2xl', '--font-size-3xl', '--font-size-4xl',
            '--line-height-tight', '--line-height-normal', '--line-height-relaxed',
            '--letter-spacing-tight', '--letter-spacing-normal', '--letter-spacing-wide',
            '--font-weight-light', '--font-weight-regular', '--font-weight-medium', '--font-weight-semibold', '--font-weight-bold',
            // Espaciado
            '--spacing-xs', '--spacing-sm', '--spacing-md', '--spacing-base', '--spacing-lg', '--spacing-xl', '--spacing-2xl', '--spacing-3xl', '--spacing-4xl',
            // Sombras
            '--shadow-sm', '--shadow-base', '--shadow-md', '--shadow-lg', '--shadow-xl',
            // Border Radius
            '--radius-sm', '--radius-base', '--radius-md', '--radius-lg', '--radius-xl', '--radius-full',
            // Transiciones
            '--transition-fast', '--transition-base', '--transition-slow'
        ];

        varNames.forEach(varName => {
            const value = styles.getPropertyValue(varName).trim();
            if (value) {
                variables[varName] = value;
            }
        });

        setCssVariables(variables);
    }, []);

    return (
        <div className="storybook-container">
            <div className="storybook-header">
                <h1 className="storybook-title">ProjetoDelta - Design System</h1>
                <p className="storybook-subtitle">Componentes e guia de estilos</p>
            </div>

            <div className="storybook-layout">
                {/* SIDEBAR: Identidade, Cores, Tipografia */}
                <aside className="storybook-sidebar">

                    {/* ========== IDENTIDADE DA MARCA ========== */}
                    <section className="storybook-section">
                        <h2 className="storybook-section-title">🎯 Identidade da Marca</h2>

                        <div className="storybook-card">
                            <h3>Logo</h3>
                            <div style={{
                                padding: '20px',
                                background: cssVariables['--color-background-light'],
                                borderRadius: '8px',
                                textAlign: 'center',
                                color: cssVariables['--color-text-muted']
                            }}>
                                <p style={{ fontSize: '13px', fontStyle: 'italic' }}>
                                    ⚠️ Por definir
                                </p>
                            </div>
                        </div>

                        <div className="storybook-card">
                            <h3>Tagline</h3>
                            <p style={{ fontStyle: 'italic', color: cssVariables['--color-text-muted'], fontSize: '13px' }}>
                                ⚠️ Por definir
                            </p>
                        </div>

                        <div className="storybook-card">
                            <h3>O Que Fazemos?</h3>
                            <p style={{ fontSize: '13px', lineHeight: '1.7', color: cssVariables['--color-text-primary'] }}>
                                <strong>ProjetoDelta</strong> é um assistente inteligente que revoluciona a gestão de projetos DevOps.
                                Conectado diretamente ao <strong>Azure DevOps</strong>, permite que as equipes consultem informações
                                sobre projetos, tarefas, horas trabalhadas e progresso através de <strong>conversas naturais</strong>.
                            </p>
                            <p style={{ fontSize: '13px', lineHeight: '1.7', color: cssVariables['--color-text-primary'], marginTop: '12px' }}>
                                Utiliza um <strong>sistema multi-agente inteligente</strong> com classificação de intenções que
                                entende o contexto, mantém memória conversacional e roteia automaticamente as consultas para
                                agentes especializados em:
                            </p>
                            <ul style={{ fontSize: '12px', lineHeight: '1.6', marginTop: '8px', paddingLeft: '20px' }}>
                                <li><strong>Busca de projetos</strong> - Encontra projetos por nome ou características</li>
                                <li><strong>Seleção de contexto</strong> - Alterna entre projetos específicos ou visão global</li>
                                <li><strong>Progresso de projetos</strong> - Estado, avanços e métricas em tempo real</li>
                                <li><strong>Horas trabalhadas</strong> - Consulta de tempo dedicado por membro ou tarefa</li>
                                <li><strong>Equipes e membros</strong> - Informações de colaboradores e papéis</li>
                                <li><strong>Atividades diárias</strong> - Resumos de trabalho e atualizações</li>
                                <li><strong>Tarefas pendentes</strong> - Work items atrasados que precisam de atenção</li>
                            </ul>
                        </div>

                        <div className="storybook-card">
                            <h3>Valores da Marca</h3>
                            <p style={{ fontStyle: 'italic', color: cssVariables['--color-text-muted'], fontSize: '13px' }}>
                                ⚠️ Por definir
                            </p>
                        </div>

                        <div className="storybook-card">
                            <h3>Personalidade da Marca</h3>
                            <p style={{ fontStyle: 'italic', color: cssVariables['--color-text-muted'], fontSize: '13px' }}>
                                ⚠️ Por definir
                            </p>
                        </div>

                        <div className="storybook-card">
                            <h3>Tom Visual</h3>
                            <p style={{ fontStyle: 'italic', color: cssVariables['--color-text-muted'], fontSize: '13px' }}>
                                ⚠️ Por definir
                            </p>
                        </div>
                    </section>

                    {/* ========== SISTEMA DE CORES ========== */}
                    <section className="storybook-section">
                        <h2 className="storybook-section-title">🎨 Cores</h2>

                        <div className="storybook-card">
                            <h3>Principais</h3>
                            <div className="color-grid">
                                {cssVariables['--color-primary'] && (
                                    <div className="color-item">
                                        <div className="color-swatch" style={{ backgroundColor: cssVariables['--color-primary'] }}></div>
                                        <p className="color-name">{cssVariables['--color-primary']}</p>
                                        <p className="color-info">Primary</p>
                                    </div>
                                )}
                                {cssVariables['--color-secondary'] && (
                                    <div className="color-item">
                                        <div className="color-swatch" style={{ backgroundColor: cssVariables['--color-secondary'] }}></div>
                                        <p className="color-name">{cssVariables['--color-secondary']}</p>
                                        <p className="color-info">Secondary</p>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="storybook-card">
                            <h3>Estados</h3>
                            <div className="color-grid">
                                {cssVariables['--color-success'] && (
                                    <div className="color-item">
                                        <div className="color-swatch" style={{ backgroundColor: cssVariables['--color-success'] }}></div>
                                        <p className="color-name">{cssVariables['--color-success']}</p>
                                        <p className="color-info">Success</p>
                                    </div>
                                )}
                                {cssVariables['--color-warning'] && (
                                    <div className="color-item">
                                        <div className="color-swatch" style={{ backgroundColor: cssVariables['--color-warning'] }}></div>
                                        <p className="color-name">{cssVariables['--color-warning']}</p>
                                        <p className="color-info">Warning</p>
                                    </div>
                                )}
                                {cssVariables['--color-error'] && (
                                    <div className="color-item">
                                        <div className="color-swatch" style={{ backgroundColor: cssVariables['--color-error'] }}></div>
                                        <p className="color-name">{cssVariables['--color-error']}</p>
                                        <p className="color-info">Error</p>
                                    </div>
                                )}
                                {cssVariables['--color-info'] && (
                                    <div className="color-item">
                                        <div className="color-swatch" style={{ backgroundColor: cssVariables['--color-info'] }}></div>
                                        <p className="color-name">{cssVariables['--color-info']}</p>
                                        <p className="color-info">Info</p>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="storybook-card">
                            <h3>Texto</h3>
                            <div className="color-grid">
                                {cssVariables['--color-text-primary'] && (
                                    <div className="color-item">
                                        <div className="color-swatch" style={{ backgroundColor: cssVariables['--color-text-primary'] }}></div>
                                        <p className="color-name">{cssVariables['--color-text-primary']}</p>
                                        <p className="color-info">Primary</p>
                                    </div>
                                )}
                                {cssVariables['--color-text-secondary'] && (
                                    <div className="color-item">
                                        <div className="color-swatch" style={{ backgroundColor: cssVariables['--color-text-secondary'] }}></div>
                                        <p className="color-name">{cssVariables['--color-text-secondary']}</p>
                                        <p className="color-info">Secondary</p>
                                    </div>
                                )}
                                {cssVariables['--color-text-muted'] && (
                                    <div className="color-item">
                                        <div className="color-swatch" style={{ backgroundColor: cssVariables['--color-text-muted'] }}></div>
                                        <p className="color-name">{cssVariables['--color-text-muted']}</p>
                                        <p className="color-info">Muted</p>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="storybook-card">
                            <h3>Fundos & Bordas</h3>
                            <div className="color-grid">
                                {cssVariables['--color-chat-bubble'] && (
                                    <div className="color-item">
                                        <div className="color-swatch" style={{ backgroundColor: cssVariables['--color-chat-bubble'] }}></div>
                                        <p className="color-name">{cssVariables['--color-chat-bubble']}</p>
                                        <p className="color-info">Bubble</p>
                                    </div>
                                )}
                                {cssVariables['--color-hover'] && (
                                    <div className="color-item">
                                        <div className="color-swatch" style={{ backgroundColor: cssVariables['--color-hover'] }}></div>
                                        <p className="color-name">{cssVariables['--color-hover']}</p>
                                        <p className="color-info">Hover</p>
                                    </div>
                                )}
                                {cssVariables['--color-border'] && (
                                    <div className="color-item">
                                        <div className="color-swatch" style={{ backgroundColor: cssVariables['--color-border'] }}></div>
                                        <p className="color-name">{cssVariables['--color-border']}</p>
                                        <p className="color-info">Border</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </section>

                    {/* ========== ICONOGRAFIA ========== */}
                    <section className="storybook-section">
                        <h2 className="storybook-section-title">📦 Iconografia</h2>

                        <div className="storybook-card">
                            <h3>Sistema de Ícones</h3>
                            <p style={{ fontSize: '13px', marginBottom: '12px' }}>
                                Estilo: <strong>Outline + Filled</strong> (Material Design compatível)
                            </p>
                        </div>

                        <div className="storybook-card">
                            <h3>Tamanhos Padrão</h3>
                            <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-end' }}>
                                <div style={{ textAlign: 'center' }}>
                                    <div style={{ fontSize: '16px' }}>📊</div>
                                    <p style={{ fontSize: '11px', margin: '4px 0 0' }}>16px</p>
                                </div>
                                <div style={{ textAlign: 'center' }}>
                                    <div style={{ fontSize: '24px' }}>📊</div>
                                    <p style={{ fontSize: '11px', margin: '4px 0 0' }}>24px</p>
                                </div>
                                <div style={{ textAlign: 'center' }}>
                                    <div style={{ fontSize: '32px' }}>📊</div>
                                    <p style={{ fontSize: '11px', margin: '4px 0 0' }}>32px</p>
                                </div>
                                <div style={{ textAlign: 'center' }}>
                                    <div style={{ fontSize: '48px' }}>📊</div>
                                    <p style={{ fontSize: '11px', margin: '4px 0 0' }}>48px</p>
                                </div>
                            </div>
                        </div>

                        <div className="storybook-card">
                            <h3>Ícones Principais</h3>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', fontSize: '24px' }}>
                                <div style={{ textAlign: 'center', padding: '8px' }}>
                                    <div>💬</div>
                                    <p style={{ fontSize: '10px', marginTop: '4px' }}>Chat</p>
                                </div>
                                <div style={{ textAlign: 'center', padding: '8px' }}>
                                    <div>📋</div>
                                    <p style={{ fontSize: '10px', marginTop: '4px' }}>Tasks</p>
                                </div>
                                <div style={{ textAlign: 'center', padding: '8px' }}>
                                    <div>👥</div>
                                    <p style={{ fontSize: '10px', marginTop: '4px' }}>Team</p>
                                </div>
                                <div style={{ textAlign: 'center', padding: '8px' }}>
                                    <div>⚙️</div>
                                    <p style={{ fontSize: '10px', marginTop: '4px' }}>Settings</p>
                                </div>
                                <div style={{ textAlign: 'center', padding: '8px' }}>
                                    <div>🔍</div>
                                    <p style={{ fontSize: '10px', marginTop: '4px' }}>Search</p>
                                </div>
                                <div style={{ textAlign: 'center', padding: '8px' }}>
                                    <div>✓</div>
                                    <p style={{ fontSize: '10px', marginTop: '4px' }}>Success</p>
                                </div>
                                <div style={{ textAlign: 'center', padding: '8px' }}>
                                    <div>⚠</div>
                                    <p style={{ fontSize: '10px', marginTop: '4px' }}>Warning</p>
                                </div>
                                <div style={{ textAlign: 'center', padding: '8px' }}>
                                    <div>📊</div>
                                    <p style={{ fontSize: '10px', marginTop: '4px' }}>Analytics</p>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* ========== TIPOGRAFIA COMPLETA ========== */}
                    <section className="storybook-section">
                        <h2 className="storybook-section-title">✏️ Tipografia</h2>

                        <div className="storybook-card">
                            <h3>Família Tipográfica</h3>
                            <p style={{ fontSize: '13px', fontFamily: cssVariables['--font-family-primary'] }}>
                                <strong>Principal:</strong> {cssVariables['--font-family-primary']?.split(',')[0]}
                            </p>
                            <p style={{ fontSize: '13px', fontFamily: cssVariables['--font-family-mono'] }}>
                                <strong>Mono:</strong> {cssVariables['--font-family-mono']?.split(',')[0]}
                            </p>
                        </div>

                        <div className="storybook-card">
                            <h3>Escala Tipográfica</h3>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                <div style={{ fontSize: cssVariables['--font-size-4xl'] }}>
                                    4XL ({cssVariables['--font-size-4xl']})
                                </div>
                                <div style={{ fontSize: cssVariables['--font-size-3xl'] }}>
                                    3XL ({cssVariables['--font-size-3xl']})
                                </div>
                                <div style={{ fontSize: cssVariables['--font-size-2xl'] }}>
                                    2XL ({cssVariables['--font-size-2xl']})
                                </div>
                                <div style={{ fontSize: cssVariables['--font-size-xl'] }}>
                                    XL ({cssVariables['--font-size-xl']})
                                </div>
                                <div style={{ fontSize: cssVariables['--font-size-lg'] }}>
                                    LG ({cssVariables['--font-size-lg']})
                                </div>
                                <div style={{ fontSize: cssVariables['--font-size-md'] }}>
                                    MD ({cssVariables['--font-size-md']})
                                </div>
                                <div style={{ fontSize: cssVariables['--font-size-base'] }}>
                                    BASE ({cssVariables['--font-size-base']})
                                </div>
                                <div style={{ fontSize: cssVariables['--font-size-sm'] }}>
                                    SM ({cssVariables['--font-size-sm']})
                                </div>
                                <div style={{ fontSize: cssVariables['--font-size-xs'] }}>
                                    XS ({cssVariables['--font-size-xs']})
                                </div>
                            </div>
                        </div>

                        <div className="storybook-card">
                            <h3>Pesos (Weights)</h3>
                            <div style={{ fontSize: '16px' }}>
                                <p style={{ fontWeight: cssVariables['--font-weight-light'] }}>Light (300)</p>
                                <p style={{ fontWeight: cssVariables['--font-weight-regular'] }}>Regular (400)</p>
                                <p style={{ fontWeight: cssVariables['--font-weight-medium'] }}>Medium (500)</p>
                                <p style={{ fontWeight: cssVariables['--font-weight-semibold'] }}>Semibold (600)</p>
                                <p style={{ fontWeight: cssVariables['--font-weight-bold'] }}>Bold (700)</p>
                            </div>
                        </div>

                        <div className="storybook-card">
                            <h3>Line Height</h3>
                            <div style={{ fontSize: '14px' }}>
                                <p style={{ lineHeight: cssVariables['--line-height-tight'], background: '#f5f5f5', padding: '4px' }}>
                                    Tight (1.2) - Para títulos grandes
                                </p>
                                <p style={{ lineHeight: cssVariables['--line-height-normal'], background: '#f5f5f5', padding: '4px', marginTop: '8px' }}>
                                    Normal (1.5) - Para cuerpos de texto
                                </p>
                                <p style={{ lineHeight: cssVariables['--line-height-relaxed'], background: '#f5f5f5', padding: '4px', marginTop: '8px' }}>
                                    Relaxed (1.8) - Para contenido extenso y lectura prolongada
                                </p>
                            </div>
                        </div>

                        <div className="storybook-card">
                            <h3>Letter Spacing</h3>
                            <div style={{ fontSize: '16px' }}>
                                <p style={{ letterSpacing: cssVariables['--letter-spacing-tight'] }}>
                                    Tight (-0.02em)
                                </p>
                                <p style={{ letterSpacing: cssVariables['--letter-spacing-normal'] }}>
                                    Normal (0)
                                </p>
                                <p style={{ letterSpacing: cssVariables['--letter-spacing-wide'] }}>
                                    Wide (0.05em)
                                </p>
                            </div>
                        </div>
                    </section>

                    {/* ========== ATIVOS VISUAIS ========== */}
                    <section className="storybook-section">
                        <h2 className="storybook-section-title">🖼️ Ativos Visuais</h2>

                        <div className="storybook-card">
                            <h3>Estilo de Ilustração</h3>
                            <p style={{ fontSize: '13px', lineHeight: '1.6' }}>
                                <strong>Flat Design</strong> com toques de isométrico. Cores sólidas do sistema.
                                Evitar gradientes complexos. Linhas limpas e formas geométricas.
                            </p>
                        </div>

                        <div className="storybook-card">
                            <h3>Padrões</h3>
                            <p style={{ fontSize: '13px', marginBottom: '8px' }}>Fundos sutis para seções:</p>
                            <div style={{
                                height: '60px',
                                background: `repeating-linear-gradient(45deg, transparent, transparent 10px, ${cssVariables['--color-background-light']} 10px, ${cssVariables['--color-background-light']} 20px)`,
                                borderRadius: '4px',
                                marginBottom: '8px'
                            }}></div>
                            <div style={{
                                height: '60px',
                                background: `radial-gradient(circle, ${cssVariables['--color-border-light']} 1px, transparent 1px)`,
                                backgroundSize: '20px 20px',
                                borderRadius: '4px'
                            }}></div>
                        </div>

                        <div className="storybook-card">
                            <h3>Estilo Fotográfico</h3>
                            <p style={{ fontSize: '13px', lineHeight: '1.6' }}>
                                <strong>Profissional e autêntico.</strong> Preferir imagens reais de equipes trabalhando.
                                Evitar stock photos genéricas. Overlay de cor primária a 10% quando necessário.
                            </p>
                        </div>
                    </section>

                    {/* ========== ESPAÇAMENTO ========== */}
                    <section className="storybook-section">
                        <h2 className="storybook-section-title">📏 Espaçamento</h2>
                        <div className="storybook-card">
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                {['xs', 'sm', 'md', 'base', 'lg', 'xl', '2xl', '3xl', '4xl'].map(size => (
                                    <div key={size} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                        <div style={{
                                            width: cssVariables[`--spacing-${size}`],
                                            height: '20px',
                                            backgroundColor: cssVariables['--color-primary'],
                                            borderRadius: '2px'
                                        }}></div>
                                        <span style={{ fontSize: '12px', fontWeight: 'bold' }}>
                                            {size.toUpperCase()} ({cssVariables[`--spacing-${size}`]})
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </section>

                    {/* ========== SOMBRAS ========== */}
                    <section className="storybook-section">
                        <h2 className="storybook-section-title">🌑 Sombras</h2>
                        <div className="storybook-card">
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                                {['sm', 'base', 'md', 'lg', 'xl'].map(size => (
                                    <div key={size} style={{
                                        padding: '16px',
                                        background: 'white',
                                        boxShadow: cssVariables[`--shadow-${size}`],
                                        borderRadius: '8px'
                                    }}>
                                        <strong style={{ fontSize: '12px' }}>{size.toUpperCase()}</strong>
                                        <p style={{ fontSize: '11px', margin: '4px 0 0', color: cssVariables['--color-text-muted'] }}>
                                            {cssVariables[`--shadow-${size}`]}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </section>

                    {/* ========== BORDER RADIUS ========== */}
                    <section className="storybook-section">
                        <h2 className="storybook-section-title">⬜ Arredondamento</h2>
                        <div className="storybook-card">
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                                {['sm', 'base', 'md', 'lg', 'xl', 'full'].map(size => (
                                    <div key={size} style={{
                                        padding: '16px',
                                        background: cssVariables['--color-background-light'],
                                        borderRadius: cssVariables[`--radius-${size}`],
                                        textAlign: 'center'
                                    }}>
                                        <strong style={{ fontSize: '11px' }}>{size.toUpperCase()}</strong>
                                        <p style={{ fontSize: '10px', margin: '4px 0 0' }}>
                                            {cssVariables[`--radius-${size}`]}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </section>

                </aside>

                {/* MAIN: Componentes */}
                <main className="storybook-main">
                    <section className="storybook-section">
                        <h2 className="storybook-section-title">Componentes</h2>

                        <div className="storybook-component-demo">
                            <div className="component-demo-header">
                                <h2>ChatBubble</h2>
                            </div>
                            <div className="component-demo-body">
                                <ChatBubble
                                    message="Hello, this is a user message"
                                    role="user"
                                    timestamp="10:30 AM"
                                />
                                <ChatBubble
                                    message="This is a system response"
                                    role="system"
                                    timestamp="10:31 AM"
                                />
                            </div>
                        </div>

                        <div className="storybook-component-demo">
                            <div className="component-demo-header">
                                <h2>ChatHeader</h2>
                            </div>
                            <div className="component-demo-body">
                                <ChatHeader
                                    title="Chat Assistant"
                                    onClear={() => alert("Clear clicked")}
                                />
                            </div>
                        </div>

                        <div className="storybook-component-demo">
                            <div className="component-demo-header">
                                <h2>ChatInput</h2>
                            </div>
                            <div className="component-demo-body">
                                <ChatInput
                                    placeholder="Type your message..."
                                    onSend={(msg) => alert(`Sent: ${msg}`)}
                                    autocompleteConfigs={[
                                        {
                                            trigger: "@",
                                            items: ["Alice", "Bob", "Charlie"],
                                            buttonLabel: "👤 Mention",
                                            onInsert: (user, msg) => `${msg}@${user} `
                                        },
                                        {
                                            trigger: "#",
                                            items: ["Project1", "Project2"],
                                            buttonLabel: "📁 Project",
                                            onInsert: (project, msg) => `${msg}#${project} `
                                        }
                                    ]}
                                />
                            </div>
                        </div>

                        <div className="storybook-component-demo">
                            <div className="component-demo-header">
                                <h2>EmptyState</h2>
                            </div>
                            <div className="component-demo-body">
                                <EmptyState />
                            </div>
                        </div>

                        <div className="storybook-component-demo">
                            <div className="component-demo-header">
                                <h2>TypingIndicator</h2>
                            </div>
                            <div className="component-demo-body">
                                <TypingIndicator />
                            </div>
                        </div>

                        <div className="storybook-component-demo">
                            <div className="component-demo-header">
                                <h2>QuickReplies</h2>
                            </div>
                            <div className="component-demo-body">
                                <QuickReplies
                                    options={["Option A", "Option B", "Option C"]}
                                    onSelect={(opt) => alert(`Selected: ${opt}`)}
                                />
                            </div>
                        </div>

                        <div className="storybook-component-demo">
                            <div className="component-demo-header">
                                <h2>AutocompleteList</h2>
                            </div>
                            <div className="component-demo-body">
                                <AutocompleteList
                                    query="a"
                                    items={["Alice", "Anna", "Bob", "Charlie"]}
                                    onSelect={(item) => alert(`Selected: ${item}`)}
                                    selectedIndex={0}
                                />
                            </div>
                        </div>

                    </section>
                </main>
            </div>
        </div>
    );
};

export default Storybook;