"""
Teste da Implementação da Fase 1 - Melhorias de Qualidade de Landmarks
Valida todos os componentes criados e suas integrações.
"""

import numpy as np
import time
import sys
import os

# Adiciona o diretório do módulo ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import ConfigManager
    from anatomical_validator import AnatomicalValidator, ValidationResult
    from smart_interpolator import SmartInterpolator, InterpolationResult
    from enhanced_landmark_processor import EnhancedLandmarkProcessor
except ImportError:
    # Fallback para importações relativas se necessário
    import importlib.util
    import sys
    
    def load_module(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    ConfigManager = load_module("config", os.path.join(base_path, "config.py")).ConfigManager
    
    anatomical_module = load_module("anatomical_validator", os.path.join(base_path, "anatomical_validator.py"))
    AnatomicalValidator = anatomical_module.AnatomicalValidator
    ValidationResult = anatomical_module.ValidationResult
    
    interpolator_module = load_module("smart_interpolator", os.path.join(base_path, "smart_interpolator.py"))
    SmartInterpolator = interpolator_module.SmartInterpolator
    InterpolationResult = interpolator_module.InterpolationResult
    
    processor_module = load_module("enhanced_landmark_processor", os.path.join(base_path, "enhanced_landmark_processor.py"))
    EnhancedLandmarkProcessor = processor_module.EnhancedLandmarkProcessor


def test_config_optimizations():
    """Testa os parâmetros otimizados de configuração."""
    print("🔧 TESTE 1: Parâmetros de Configuração Otimizados")
    print("=" * 50)
    
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    # Verifica parâmetros otimizados
    optimized_params = {
        'min_detection_confidence': 0.85,
        'min_tracking_confidence': 0.85,
        'kalman_process_noise': 0.005,
        'kalman_measurement_noise': 0.08,
        'outlier_velocity_threshold': 35.0,
        'outlier_acceleration_threshold': 75.0,
        'weighted_window_size': 7,
        'weighted_decay_factor': 0.85,
        'landmark_visibility_threshold': 0.5,
        'landmark_confidence_threshold': 0.7
    }
    
    all_correct = True
    for param, expected_value in optimized_params.items():
        actual_value = config.get(param)
        status = "✅" if actual_value == expected_value else "❌"
        print(f"{status} {param}: {actual_value} (esperado: {expected_value})")
        if actual_value != expected_value:
            all_correct = False
    
    print(f"\nResultado: {'✅ PASSOU' if all_correct else '❌ FALHOU'}")
    return all_correct


def test_anatomical_validation():
    """Testa o sistema de validação anatômica."""
    print("\n🔍 TESTE 2: Validação Anatômica")
    print("=" * 50)
    
    validator = AnatomicalValidator()
    
    # Teste 1: Landmarks válidos
    valid_landmarks = np.array([
        [0.5, 0.1, 0.0, 0.9],  # Nariz
        [0.45, 0.15, 0.0, 0.8],  # Olho esquerdo
        [0.55, 0.15, 0.0, 0.8],  # Olho direito
        [0.4, 0.2, 0.0, 0.7],   # Orelha esquerda
        [0.6, 0.2, 0.0, 0.7],   # Orelha direita
        [0.45, 0.25, 0.0, 0.8], # Ombro esquerdo
        [0.55, 0.25, 0.0, 0.8], # Ombro direito
        [0.4, 0.4, 0.0, 0.7],   # Cotovelo esquerdo
        [0.6, 0.4, 0.0, 0.7],   # Cotovelo direito
        [0.35, 0.55, 0.0, 0.6], # Pulso esquerdo
        [0.65, 0.55, 0.0, 0.6], # Pulso direito
        [0.48, 0.6, 0.0, 0.8],  # Quadril esquerdo
        [0.52, 0.6, 0.0, 0.8],  # Quadril direito
        [0.46, 0.8, 0.0, 0.7],  # Joelho esquerdo
        [0.54, 0.8, 0.0, 0.7],  # Joelho direito
        [0.45, 1.0, 0.0, 0.6],  # Tornozelo esquerdo
        [0.55, 1.0, 0.0, 0.6],  # Tornozelo direito
    ] + [[0.5, 0.5, 0.0, 0.5]] * 16)  # Preenche até 33 landmarks
    
    result_valid = validator.validate_landmarks(valid_landmarks)
    print(f"✅ Landmarks válidos: {'PASSOU' if result_valid.is_valid else 'FALHOU'}")
    print(f"   Confiança: {result_valid.confidence_score:.3f}")
    
    # Teste 2: Landmarks inválidos (proporções impossíveis)
    invalid_landmarks = valid_landmarks.copy()
    invalid_landmarks[5] = [0.1, 0.25, 0.0, 0.8]  # Ombro muito longe
    invalid_landmarks[6] = [0.9, 0.25, 0.0, 0.8]  # Ombro muito longe
    
    result_invalid = validator.validate_landmarks(invalid_landmarks)
    print(f"✅ Landmarks inválidos detectados: {'PASSOU' if not result_invalid.is_valid else 'FALHOU'}")
    print(f"   Problemas encontrados: {len(result_invalid.issues)}")
    
    return result_valid.is_valid and not result_invalid.is_valid


def test_smart_interpolation():
    """Testa o sistema de interpolação inteligente."""
    print("\n🔄 TESTE 3: Interpolação Inteligente")
    print("=" * 50)
    
    interpolator = SmartInterpolator(history_size=5)
    
    # Cria landmarks com alguns ausentes
    landmarks = np.random.rand(33, 4)
    landmarks[10] = np.nan  # Pulso ausente
    landmarks[15] = [0.0, 0.0, 0.0, 0.1]  # Baixa visibilidade
    
    # Adiciona histórico
    for i in range(3):
        hist_landmarks = np.random.rand(33, 4)
        interpolator.update_history(hist_landmarks, time.time() - (3-i))
    
    # Testa interpolação
    missing_indices = [10, 15]
    result = interpolator.interpolate_missing_landmarks(landmarks, missing_indices)
    
    print(f"✅ Interpolação executada: {'PASSOU' if result.success else 'FALHOU'}")
    print(f"   Método usado: {result.method_used}")
    print(f"   Confiança: {result.confidence:.3f}")
    print(f"   Landmarks interpolados: {len(result.interpolated_indices)}")
    
    return result.success


def test_enhanced_processor():
    """Testa o processador aprimorado integrado."""
    print("\n🚀 TESTE 4: Processador Aprimorado Integrado")
    print("=" * 50)
    
    # Cria processador com configurações otimizadas
    processor = EnhancedLandmarkProcessor()
    
    # Teste com landmarks de qualidade variada
    test_cases = [
        ("Landmarks de alta qualidade", np.random.rand(33, 4) * 0.8 + 0.2),
        ("Landmarks com ausentes", _create_landmarks_with_missing()),
        ("Landmarks de baixa qualidade", np.random.rand(33, 4) * 0.3),
    ]
    
    all_passed = True
    
    for test_name, landmarks in test_cases:
        result = processor.process_landmarks(landmarks)
        
        passed = (result.quality_score > 0.0 and 
                 result.processing_time < 0.1 and  # Menos de 100ms
                 len(result.notes) > 0)
        
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{status} {test_name}")
        print(f"   Qualidade: {result.quality_score:.3f}")
        print(f"   Tempo: {result.processing_time*1000:.1f}ms")
        print(f"   Notas: {len(result.notes)} observações")
        
        if not passed:
            all_passed = False
    
    # Testa estatísticas
    stats = processor.get_processing_stats()
    print(f"\n📊 Estatísticas após {stats['total_frames']} frames:")
    print(f"   Qualidade média: {stats['average_quality_score']:.3f}")
    print(f"   Tempo médio: {stats['average_processing_time']*1000:.1f}ms")
    
    return all_passed


def _create_landmarks_with_missing():
    """Cria landmarks com alguns ausentes para teste."""
    landmarks = np.random.rand(33, 4)
    landmarks[5] = np.nan  # Ombro ausente
    landmarks[10] = [0.0, 0.0, 0.0, 0.1]  # Baixa visibilidade
    landmarks[15] = np.nan  # Tornozelo ausente
    return landmarks


def test_performance_benchmark():
    """Testa performance do sistema completo."""
    print("\n⚡ TESTE 5: Benchmark de Performance")
    print("=" * 50)
    
    processor = EnhancedLandmarkProcessor()
    
    # Teste de performance com 100 frames
    num_frames = 100
    total_time = 0
    
    print(f"Processando {num_frames} frames...")
    
    for i in range(num_frames):
        landmarks = np.random.rand(33, 4)
        if i % 10 == 0:  # 10% com landmarks ausentes
            landmarks[np.random.randint(0, 33)] = np.nan
        
        start_time = time.time()
        result = processor.process_landmarks(landmarks)
        total_time += time.time() - start_time
    
    avg_time = total_time / num_frames
    fps = 1.0 / avg_time if avg_time > 0 else 0
    
    print(f"✅ Tempo médio por frame: {avg_time*1000:.2f}ms")
    print(f"✅ FPS estimado: {fps:.1f}")
    print(f"✅ Performance: {'EXCELENTE' if fps > 30 else 'BOA' if fps > 15 else 'PRECISA MELHORAR'}")
    
    # Relatório final
    print("\n" + processor.get_quality_report())
    
    return fps > 10  # Pelo menos 10 FPS


def run_all_tests():
    """Executa todos os testes da Fase 1."""
    print("🧪 INICIANDO TESTES DA FASE 1 - MELHORIAS DE QUALIDADE")
    print("=" * 60)
    
    tests = [
        ("Configurações Otimizadas", test_config_optimizations),
        ("Validação Anatômica", test_anatomical_validation),
        ("Interpolação Inteligente", test_smart_interpolation),
        ("Processador Integrado", test_enhanced_processor),
        ("Benchmark de Performance", test_performance_benchmark),
    ]
    
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERRO em {test_name}: {str(e)}")
            results.append((test_name, False))
    
    total_time = time.time() - start_time
    
    # Relatório final
    print("\n" + "="*60)
    print("📋 RELATÓRIO FINAL DOS TESTES")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 RESULTADO GERAL: {passed}/{total} testes passaram")
    print(f"⏱️  Tempo total: {total_time:.2f}s")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Fase 1 implementada com sucesso!")
    else:
        print("⚠️  Alguns testes falharam. Revisar implementação.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)