import { Modal, Form, Input, Select, message } from 'antd'
import { useState, useEffect } from 'react'
import { apiKeyService } from '../../services'
import { useChatStore } from '../../store/chatStore'
import type { APIKey, ConversationCreate } from '../../types'

interface NewConversationModalProps {
  visible: boolean
  onClose: () => void
}

export default function NewConversationModal({ visible, onClose }: NewConversationModalProps) {
  const { createConversation } = useChatStore()
  const [form] = Form.useForm()
  const [apiKeys, setApiKeys] = useState<APIKey[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (visible) {
      fetchAPIKeys()
    }
  }, [visible])

  const fetchAPIKeys = async () => {
    try {
      const keys = await apiKeyService.getAPIKeys()
      const activeKeys = keys.filter((k) => k.is_active)
      setApiKeys(activeKeys)

      if (activeKeys.length === 1) {
        form.setFieldsValue({ api_key_id: activeKeys[0].id })
      }
    } catch (error: any) {
      message.error('获取 API Keys 失败')
    }
  }

  const handleSubmit = async () => {
    try {
      setLoading(true)
      const values = await form.validateFields()

      const data: ConversationCreate = {
        title: values.title,
        model: values.model,
        api_key_id: values.api_key_id,
        system_prompt: values.system_prompt || undefined,
      }

      await createConversation(data)
      message.success('对话创建成功')
      form.resetFields()
      onClose()
    } catch (error: any) {
      if (!error.errorFields) {
        message.error('创建失败')
      }
    } finally {
      setLoading(false)
    }
  }

  const getModelsByAPIKey = (apiKeyId: number) => {
    const apiKey = apiKeys.find((k) => k.id === apiKeyId)
    if (!apiKey) return []

    const modelsByProvider: Record<string, string[]> = {
      openai: ['gpt-4', 'gpt-4-turbo-preview', 'gpt-3.5-turbo'],
      anthropic: ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
      google: ['gemini-pro', 'gemini-pro-vision'],
      ollama: ['llama2', 'mistral', 'codellama'],
    }

    return modelsByProvider[apiKey.provider] || []
  }

  return (
    <Modal
      title="创建新对话"
      open={visible}
      onOk={handleSubmit}
      onCancel={() => {
        form.resetFields()
        onClose()
      }}
      confirmLoading={loading}
      width={600}
    >
      <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
        <Form.Item
          name="title"
          label="对话标题"
          rules={[
            { required: true, message: '请输入对话标题' },
            { max: 200, message: '标题最多200个字符' },
          ]}
        >
          <Input placeholder="例如: 数据分析助手" />
        </Form.Item>

        <Form.Item
          name="api_key_id"
          label="API Key"
          rules={[{ required: true, message: '请选择 API Key' }]}
        >
          <Select
            placeholder="选择要使用的 API Key"
            options={apiKeys.map((key) => ({
              value: key.id,
              label: `${key.name} (${key.provider})`,
            }))}
            onChange={() => form.setFieldsValue({ model: undefined })}
          />
        </Form.Item>

        <Form.Item
          noStyle
          shouldUpdate={(prev, curr) => prev.api_key_id !== curr.api_key_id}
        >
          {({ getFieldValue }) => {
            const apiKeyId = getFieldValue('api_key_id')
            const models = apiKeyId ? getModelsByAPIKey(apiKeyId) : []

            return (
              <Form.Item
                name="model"
                label="模型"
                rules={[{ required: true, message: '请选择模型' }]}
              >
                <Select
                  placeholder="选择模型"
                  disabled={!apiKeyId}
                  options={models.map((model) => ({
                    value: model,
                    label: model,
                  }))}
                />
              </Form.Item>
            )
          }}
        </Form.Item>

        <Form.Item name="system_prompt" label="系统提示词 (可选)">
          <Input.TextArea
            placeholder="例如: 你是一个专业的数据分析助手..."
            rows={3}
          />
        </Form.Item>
      </Form>

      {apiKeys.length === 0 && (
        <div style={{ marginTop: 16, padding: 12, background: '#fff7e6', borderRadius: 4 }}>
          <span>
            还没有可用的 API Key,请先到{' '}
            <a href="/api-keys" target="_blank" rel="noopener noreferrer">
              API Keys 管理
            </a>{' '}
            页面添加
          </span>
        </div>
      )}
    </Modal>
  )
}
