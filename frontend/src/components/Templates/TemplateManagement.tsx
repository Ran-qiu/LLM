import { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Switch,
  message,
  Space,
  Tag,
  Popconfirm,
  Typography,
} from 'antd'
import {
  FileTextOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  StarOutlined,
} from '@ant-design/icons'
import { templateService } from '../../services'
import type { Template, TemplateCreate, TemplateUpdate } from '../../types'
import { formatDate } from '../../utils/format'
import type { ColumnsType } from 'antd/es/table'

const { Title, Paragraph } = Typography
const { TextArea } = Input

export default function TemplateManagement() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    fetchTemplates()
  }, [])

  const fetchTemplates = async () => {
    setLoading(true)
    try {
      const data = await templateService.getTemplates()
      setTemplates(data)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取模板失败')
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setEditingTemplate(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: Template) => {
    setEditingTemplate(record)
    form.setFieldsValue({
      name: record.name,
      description: record.description,
      title_template: record.title_template,
      model: record.model,
      system_prompt: record.system_prompt,
      is_public: record.is_public,
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await templateService.deleteTemplate(id)
      message.success('删除成功')
      fetchTemplates()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败')
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()

      if (editingTemplate) {
        await templateService.updateTemplate(editingTemplate.id, values as TemplateUpdate)
        message.success('更新成功')
      } else {
        await templateService.createTemplate(values as TemplateCreate)
        message.success('添加成功')
      }

      setModalVisible(false)
      form.resetFields()
      fetchTemplates()
    } catch (error: any) {
      if (error.errorFields) {
        return
      }
      message.error(error.response?.data?.detail || '操作失败')
    }
  }

  const columns: ColumnsType<Template> = [
    {
      title: '模板名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: Template) => (
        <Space>
          {name}
          {record.is_public && <Tag color="blue">公开</Tag>}
        </Space>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '模型',
      dataIndex: 'model',
      key: 'model',
    },
    {
      title: '使用次数',
      dataIndex: 'usage_count',
      key: 'usage_count',
      render: (count: number) => (
        <Space>
          <StarOutlined style={{ color: '#faad14' }} />
          {count}
        </Space>
      ),
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
            title="确定删除此模板吗?"
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
            <FileTextOutlined />
            <Title level={4} style={{ margin: 0 }}>模板管理</Title>
          </Space>
        }
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            添加模板
          </Button>
        }
      >
        <Paragraph type="secondary">
          创建对话模板,快速开始特定类型的对话。公开的模板可以被所有用户使用。
        </Paragraph>
        <Table
          columns={columns}
          dataSource={templates}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={editingTemplate ? '编辑模板' : '添加模板'}
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
            name="name"
            label="模板名称"
            rules={[
              { required: true, message: '请输入模板名称' },
              { max: 100, message: '名称最多100个字符' },
            ]}
          >
            <Input placeholder="例如: 代码审查助手" />
          </Form.Item>

          <Form.Item name="description" label="描述">
            <TextArea rows={2} placeholder="简要描述此模板的用途" />
          </Form.Item>

          <Form.Item
            name="title_template"
            label="对话标题模板"
            rules={[{ required: true, message: '请输入标题模板' }]}
          >
            <Input placeholder="例如: 代码审查 - {date}" />
          </Form.Item>

          <Form.Item
            name="model"
            label="默认模型"
            rules={[{ required: true, message: '请输入模型名称' }]}
          >
            <Input placeholder="例如: gpt-4" />
          </Form.Item>

          <Form.Item name="system_prompt" label="系统提示词">
            <TextArea
              rows={4}
              placeholder="定义 AI 助手的角色和行为..."
            />
          </Form.Item>

          <Form.Item
            name="is_public"
            label="公开模板"
            valuePropName="checked"
            initialValue={false}
          >
            <Switch checkedChildren="公开" unCheckedChildren="私有" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
