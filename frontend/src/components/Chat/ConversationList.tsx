import { useState, useEffect } from 'react'
import {
  List,
  Button,
  Input,
  Typography,
  Popconfirm,
  Space,
  Empty,
  Spin,
  message,
  Modal,
  Form,
} from 'antd'
import {
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  MessageOutlined,
} from '@ant-design/icons'
import { useChatStore } from '../../store/chatStore'
import { formatRelativeTime, truncate } from '../../utils/format'
import type { Conversation } from '../../types'

const { Text } = Typography
const { Search } = Input

interface ConversationListProps {
  onNewConversation: () => void
}

export default function ConversationList({ onNewConversation }: ConversationListProps) {
  const {
    conversations,
    currentConversation,
    isLoading,
    fetchConversations,
    selectConversation,
    updateConversation,
    deleteConversation,
  } = useChatStore()

  const [searchQuery, setSearchQuery] = useState('')
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [editingConversation, setEditingConversation] = useState<Conversation | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    fetchConversations()
  }, [fetchConversations])

  const filteredConversations = conversations.filter((conv) =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleSelect = (id: number) => {
    selectConversation(id)
  }

  const handleEdit = (conv: Conversation, e: React.MouseEvent) => {
    e.stopPropagation()
    setEditingConversation(conv)
    form.setFieldsValue({ title: conv.title })
    setEditModalVisible(true)
  }

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await deleteConversation(id)
      message.success('对话已删除')
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleUpdateTitle = async () => {
    if (!editingConversation) return

    try {
      const values = await form.validateFields()
      await updateConversation(editingConversation.id, values.title)
      message.success('标题已更新')
      setEditModalVisible(false)
      setEditingConversation(null)
    } catch (error: any) {
      if (!error.errorFields) {
        message.error('更新失败')
      }
    }
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', background: '#fff' }}>
      <div style={{ padding: 16 }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          block
          onClick={onNewConversation}
          style={{ marginBottom: 12 }}
        >
          新建对话
        </Button>
        <Search
          placeholder="搜索对话"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          allowClear
        />
      </div>

      <div style={{ flex: 1, overflow: 'auto' }}>
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: 32 }}>
            <Spin />
          </div>
        ) : filteredConversations.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="暂无对话"
            style={{ marginTop: 32 }}
          />
        ) : (
          <List
            dataSource={filteredConversations}
            renderItem={(conv) => (
              <List.Item
                key={conv.id}
                onClick={() => handleSelect(conv.id)}
                style={{
                  cursor: 'pointer',
                  background: currentConversation?.id === conv.id ? '#e6f7ff' : 'transparent',
                  padding: '12px 16px',
                  borderLeft:
                    currentConversation?.id === conv.id ? '3px solid #1890ff' : '3px solid transparent',
                }}
                actions={[
                  <Button
                    key="edit"
                    type="text"
                    size="small"
                    icon={<EditOutlined />}
                    onClick={(e) => handleEdit(conv, e)}
                  />,
                  <Popconfirm
                    key="delete"
                    title="确定删除此对话吗?"
                    description="删除后将无法恢复"
                    onConfirm={(e) => handleDelete(conv.id, e!)}
                    onCancel={(e) => e?.stopPropagation()}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Button
                      type="text"
                      size="small"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </Popconfirm>,
                ]}
              >
                <List.Item.Meta
                  avatar={<MessageOutlined style={{ fontSize: 20, color: '#1890ff' }} />}
                  title={<Text strong>{truncate(conv.title, 30)}</Text>}
                  description={
                    <Space direction="vertical" size={0}>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {conv.model}
                      </Text>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {formatRelativeTime(conv.updated_at)}
                      </Text>
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </div>

      <Modal
        title="编辑对话标题"
        open={editModalVisible}
        onOk={handleUpdateTitle}
        onCancel={() => {
          setEditModalVisible(false)
          setEditingConversation(null)
        }}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="title"
            label="标题"
            rules={[
              { required: true, message: '请输入标题' },
              { max: 200, message: '标题最多200个字符' },
            ]}
          >
            <Input placeholder="输入对话标题" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
