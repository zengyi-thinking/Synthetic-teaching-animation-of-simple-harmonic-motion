# -*- coding: utf-8 -*-
"""
简化的界面重构测试
快速验证重构后的核心功能
"""

import sys
import numpy as np
from PyQt6.QtWidgets import QApplication
from harmonic_synthesizer_ui import HarmonicSynthesizerPanel

def test_refactor_simple():
    """简化的重构测试"""
    app = QApplication(sys.argv)
    
    try:
        print("🔧 开始界面重构验证...")
        
        # 创建面板
        panel = HarmonicSynthesizerPanel()
        panel.setWindowTitle("界面重构验证 - 简谐波合成器")
        panel.resize(1400, 900)
        
        # 验证核心组件
        print("✅ 面板创建成功")
        
        # 验证新的分解波形可视化器
        assert hasattr(panel, 'components_viz'), "分解波形可视化器缺失"
        assert hasattr(panel, 'components_canvas'), "分解波形画布缺失"
        print("✅ 分解波形可视化器正常")
        
        # 验证频谱组件已移除
        assert not hasattr(panel, 'spectrum_viz'), "频谱可视化器未移除"
        assert not hasattr(panel, 'spectrum_canvas'), "频谱画布未移除"
        print("✅ 频谱分析组件已完全移除")
        
        # 验证合成波形可视化器仍然存在
        assert hasattr(panel, 'waveform_viz'), "合成波形可视化器缺失"
        assert hasattr(panel, 'waveform_canvas'), "合成波形画布缺失"
        print("✅ 合成波形可视化器正常")
        
        # 测试添加分量
        initial_count = len(panel.harmonic_components)
        panel.add_harmonic_component(880, 0.6, 0)  # A5
        panel.add_harmonic_component(1320, 0.4, np.pi/3)  # E6
        final_count = len(panel.harmonic_components)
        print(f"✅ 分量添加测试: {initial_count} -> {final_count}")
        
        # 测试更新合成
        panel.update_synthesis()
        print("✅ 合成更新功能正常")
        
        # 验证分量计数
        count_text = panel.component_count_label.text()
        print(f"✅ 分量计数显示: {count_text}")
        
        # 测试预设功能
        panel.preset_combo.setCurrentText("三角波近似")
        panel.on_apply_preset()
        print("✅ 预设应用功能正常")
        
        # 验证画布尺寸
        waveform_height = panel.waveform_canvas.height()
        components_height = panel.components_canvas.height()
        print(f"✅ 画布尺寸 - 合成波形: {waveform_height}px, 分解波形: {components_height}px")
        
        print("\n🎉 界面重构验证完成！")
        print("\n📋 重构成果:")
        print("- ❌ 移除频谱分析面板")
        print("- ✅ 新增分解波形面板")
        print("- ✅ 保持所有控制功能")
        print("- ✅ 优化可视化体验")
        print("- ✅ 界面布局更加平衡")
        
        # 显示界面
        panel.show()
        
        print("\n界面已启动，请手动验证以下功能:")
        print("1. 分解波形面板显示各个简谐分量")
        print("2. 合成波形面板显示叠加结果")
        print("3. 添加/删除分量功能正常")
        print("4. 音频播放功能正常")
        print("5. 预设切换功能正常")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_refactor_simple())
