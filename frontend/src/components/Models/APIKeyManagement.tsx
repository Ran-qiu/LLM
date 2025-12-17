import { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  message,
  Space,
  Tag,
  Popconfirm,
  Typography,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  KeyOutlined,
} from '@ant-design/icons'
import { apiKeyService } from '../../services'
import { APIKey, APIKeyCreate, APIKeyUpdate } from '../../types'
import { formatDate, getProviderName } from '../../utils/format'
import type { ColumnsType } from 'antd/es/table'

const { Title } = Typography

const PROVIDERS = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'google', label: 'Google' },
  { value: 'ollama', label: 'Ollama' },
  { value: 'custom', label: '自定义' },
]

export default function APIKeyManagement() {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingKey, setEditingKey] = useState<APIKey | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    fetchAPIKeys()
  }, [])

  const fetchAPIKeys = async () => {
    setLoading(true)
    try {
      const data = await apiKeyService.getAPIKeys()
      setApiKeys(data)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取 API Keys 失败')
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setEditingKey(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: APIKey) => {
    setEditingKey(record)
    form.setFieldsValue({
      provider: record.provider,
      name: record.name,
      is_active: record.is_active,
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await apiKeyService.deleteAPIKey(id)
      message.success('删除成功')
      fetchAPIKeys()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败')
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()

      if (editingKey) {
        // Update existing key
        const updateData: APIKeyUpdate = {
          name: values.name,
          is_active: values.is_active,
        }
        if (values.api_key) {
          updateData.api_key = values.api_key
        }
        if (values.base_url) {
          updateData.base_url = values.base_url
        }
        if (values.model_name) {
          updateData.model_name = values.model_name
        }

        await apiKeyService.updateAPIKey(editingKey.id, updateData)
        message.success('更新成功')
      } else {
        // Create new key
        const createData: APIKeyCreate = {
          provider: values.provider,
          name: values.name,
          api_key: values.api_key,
        }
        if (values.base_url) {
          createData.base_url = values.base_url
        }
        if (values.model_name) {
          createData.model_name = values.model_name
        }

        await apiKeyService.createAPIKey(createData)
        message.success('添加成功')
      }

      setModalVisible(false)
      form.resetFields()
      fetchAPIKeys()
    } catch (error: any) {
      if (error.errorFields) {
        // Form validation error
        return
      }
      message.error(error.response?.data?.detail || '操作失败')
    }
  }

  const columns: ColumnsType<APIKey> = [
    {
      title: '提供商',
      dataIndex: 'provider',
      key: 'provider',
      render: (provider: string) => (
        <Tag color="blue">{getProviderName(provider)}</Tag>
      ),
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'success' : 'default'}>
          {isActive ? '激活' : '停用'}
        </Tag>
      ),
    },
    {
      title: '最后使用',
      dataIndex: 'last_used_at',
      key: 'last_used_at',
      render: (date: string) => (date ? formatDate(date) : '-'),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => formatDate(date),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此 API Key 吗?"
            description="删除后将无法恢复"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Card
        title={
          <Space>
            <KeyOutlined />
            <Title level={4} style={{ margin: 0 }}>API Key 管理</Title>
          </Space>
        }
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            添加 API Key
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={apiKeys}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={editingKey ? '编辑 API Key' : '添加 API Key'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="provider"
            label="提供商"
            rules={[{ required: true, message: '请选择提供商' }]}
          >
            <Select
              options={PROVIDERS}
              disabled={!!editingKey}
              placeholder="选择 LLM 提供商"
            />
          </Form.Item>

          <Form.Item
            name="name"
            label="名称"
            rules={[
              { required: true, message: '请输入名称' },
              { max: 100, message: '名称最多100个字符' },
            ]}
          >
            <Input placeholder="例如: OpenAI GPT-4" />
          </Form.Item>

          <Form.Item
            name="api_key"
            label="API Key"
            rules={
              editingKey
                ? []
                : [{ required: true, message: '请输入 API Key' }]
            }
            help={editingKey ? '留空则不更新 API Key' : undefined}
          >
            <Input.Password placeholder="输入您的 API Key" />
          </Form.Item>

          <Form.Item
            noStyle
            shouldUpdate={(prevValues, currentValues) =>
              prevValues.provider !== currentValues.provider
            }
          >
            {({ getFieldValue }) =>
              (getFieldValue('provider') === 'ollama' ||
                getFieldValue('provider') === 'custom') ? (
                <>
                  <Form.Item name="base_url" label="Base URL">
                    <Input placeholder="例如: http://localhost:11434" />
                  </Form.Item>
                  <Form.Item name="model_name" label="模型名称">
                    <Input placeholder="例如: llama2" />
                  </Form.Item>
                </>
              ) : null
            }
          </Form.Item>

          {editingKey && (
            <Form.Item
              name="is_active"
              label="状态"
              valuePropName="checked"
              initialValue={true}
            >
              <Switch checkedChildren="激活" unCheckedChildren="停用" />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </div>
  )
}
