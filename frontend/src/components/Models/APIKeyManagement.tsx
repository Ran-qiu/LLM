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
  Collapse,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  KeyOutlined,
  InfoCircleOutlined,
  GatewayOutlined,
  GlobalOutlined,
  CloudServerOutlined,
  ClusterOutlined,
} from '@ant-design/icons'
import { apiKeyService } from '../../services'
import { APIKey, APIKeyCreate, APIKeyUpdate } from '../../types'
import { formatDate } from '../../utils/format'
import type { ColumnsType } from 'antd/es/table'

const { Title, Text } = Typography
const { Panel } = Collapse

const PROVIDERS = [
  { value: 'openai', label: 'OpenAI', icon: <GlobalOutlined /> },
  { value: 'anthropic', label: 'Anthropic', icon: <CloudServerOutlined /> },
  { value: 'google', label: 'Google', icon: <GlobalOutlined /> },
  { value: 'ollama', label: 'Ollama', icon: <ClusterOutlined /> },
  { value: 'gateway_client', label: '网关客户端凭证', icon: <GatewayOutlined /> },
  { value: 'custom', label: '自定义', icon: <GlobalOutlined /> },
]

interface GroupedKeys {
  [provider: string]: APIKey[]
}

export default function APIKeyManagement() {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([])
  const [modalVisible, setModalVisible] = useState(false)
  const [editingKey, setEditingKey] = useState<APIKey | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    fetchAPIKeys()
  }, [])

  const fetchAPIKeys = async () => {
    try {
      const data = await apiKeyService.getAPIKeys()
      setApiKeys(data)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取 API Keys 失败')
    }
  }

  const handleAdd = (provider?: string) => {
    setEditingKey(null)
    form.resetFields()
    if (provider) {
      form.setFieldValue('provider', provider)
    }
    setModalVisible(true)
  }

  const handleEdit = (record: APIKey) => {
    setEditingKey(record)
    // Extract base_url and model_name from custom_config if available
    const customConfig = record.custom_config || {}
    
    form.setFieldsValue({
      provider: record.provider,
      name: record.name,
      api_key: undefined, // Don't show existing key
      is_active: record.is_active,
      rpm_limit: record.rpm_limit,
      base_url: customConfig.base_url,
      model_name: customConfig.model_name,
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

      // Construct custom_config
      const customConfig: any = {}
      if (values.base_url) customConfig.base_url = values.base_url
      if (values.model_name) customConfig.model_name = values.model_name

      if (editingKey) {
        // Update existing key
        const updateData: APIKeyUpdate = {
          name: values.name,
          is_active: values.is_active,
          rpm_limit: Number(values.rpm_limit),
          custom_config: Object.keys(customConfig).length > 0 ? customConfig : undefined,
        }
        if (values.api_key) {
          updateData.api_key = values.api_key
        }

        await apiKeyService.updateAPIKey(editingKey.id, updateData)
        message.success('更新成功')
      } else {
        // Create new key
        const createData: APIKeyCreate = {
          provider: values.provider,
          name: values.name,
          api_key: values.api_key,
          rpm_limit: Number(values.rpm_limit),
          custom_config: Object.keys(customConfig).length > 0 ? customConfig : undefined,
        }

        await apiKeyService.createAPIKey(createData)
        message.success('添加成功')
      }

      setModalVisible(false)
      form.resetFields()
      fetchAPIKeys()
    } catch (error: any) {
      if (error.errorFields) {
        return
      }
      message.error(error.response?.data?.detail || '操作失败')
    }
  }

  const columns: ColumnsType<APIKey> = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
           <span>{text}</span>
           {record.provider === 'ollama' && record.custom_config?.base_url && (
             <Tag>{record.custom_config.base_url}</Tag>
           )}
        </Space>
      )
    },
    {
      title: 'RPM 限制',
      dataIndex: 'rpm_limit',
      key: 'rpm_limit',
      render: (rpm) => rpm > 0 ? rpm : '无限制',
      width: 100,
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
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
      width: 150,
      render: (date: string) => (date ? formatDate(date) : '-'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
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
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  // Group keys by provider
  const groupedKeys: GroupedKeys = {}
  PROVIDERS.forEach(p => {
    groupedKeys[p.value] = []
  })
  
  apiKeys.forEach(key => {
    if (!groupedKeys[key.provider]) {
      groupedKeys[key.provider] = []
    }
    groupedKeys[key.provider].push(key)
  })

  // Calculate stats for header
  const getProviderStats = (provider: string, keys: APIKey[]) => {
    const activeKeys = keys.filter(k => k.is_active).length
    const totalRpm = keys.reduce((sum, k) => sum + (k.is_active ? k.rpm_limit : 0), 0)
    
    let statusText = "未配置"
    let statusColor = "default"
    
    if (activeKeys === 1) {
      statusText = "单 Key 模式"
      statusColor = "blue"
    } else if (activeKeys > 1) {
      statusText = `号池模式 (${activeKeys} 活跃)`
      statusColor = "green"
    }

    if (provider === 'gateway_client') {
       statusText = `${activeKeys} 个客户端`
       statusColor = activeKeys > 0 ? "purple" : "default"
    }

    return (
      <Space split="|">
        <Tag color={statusColor}>{statusText}</Tag>
        {provider !== 'gateway_client' && activeKeys > 0 && (
           <Text type="secondary" style={{ fontSize: 12 }}>
             总 RPM 容量: {totalRpm > 0 ? totalRpm : '∞'}
           </Text>
        )}
      </Space>
    )
  }

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
          <Button type="primary" icon={<PlusOutlined />} onClick={() => handleAdd()}>
            添加 API Key
          </Button>
        }
      >
        <Collapse 
            defaultActiveKey={['openai']} 
            ghost
            expandIconPosition="end"
        >
          {PROVIDERS.map((provider) => {
             const keys = groupedKeys[provider.value] || []
             return (
               <Panel
                 key={provider.value}
                 header={
                   <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                     <Space size="large">
                        <Space>
                            {provider.icon}
                            <Text strong>{provider.label}</Text>
                        </Space>
                        {getProviderStats(provider.value, keys)}
                     </Space>
                     {/* Prevent click propagation to collapse */}
                     <div onClick={(e) => e.stopPropagation()}>
                        <Button 
                            size="small" 
                            type="dashed" 
                            icon={<PlusOutlined />}
                            onClick={() => handleAdd(provider.value)}
                        >
                            添加
                        </Button>
                     </div>
                   </div>
                 }
               >
                 <Table
                    columns={columns}
                    dataSource={keys}
                    rowKey="id"
                    pagination={false}
                    size="small"
                    locale={{ emptyText: '暂无配置，点击右上角添加' }}
                 />
               </Panel>
             )
          })}
        </Collapse>
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
            noStyle
            shouldUpdate={(prevValues, currentValues) =>
              prevValues.provider !== currentValues.provider
            }
          >
            {({ getFieldValue }) =>
              getFieldValue('provider') === 'gateway_client' ? (
                 // Gateway Client Specific Fields
                 <Form.Item>
                    <div style={{ color: '#888', marginBottom: 10 }}>
                        <InfoCircleOutlined /> 网关客户端凭证用于让其他应用程序（如 LobeChat, NextChat）连接到此系统。
                    </div>
                 </Form.Item>
              ) : (
                // Normal Provider Fields
                <Form.Item
                    name="rpm_limit"
                    label="每分钟最大请求数 (RPM Limit)"
                    initialValue={60}
                    rules={[{ required: true, message: '请输入 RPM 限制' }]}
                    help="设置该 Key 每分钟允许的最大调用次数，0 为不限制"
                >
                    <Input type="number" min={0} />
                </Form.Item>
              )
            }
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
            <Input.Password placeholder="输入您的 API Key (sk-...)" />
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