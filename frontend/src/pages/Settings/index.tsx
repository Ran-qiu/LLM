import React, { useState, useEffect } from 'react'
import { Card, Form, Input, Button, Tabs, message, Popconfirm, Alert } from 'antd'
import { UserOutlined, LockOutlined, SaveOutlined, DeleteOutlined } from '@ant-design/icons'
import { authService } from '../../services/authService'
import { userService } from '../../services/userService'
import { User } from '../../types'
import { useAuthStore } from '../../store/authStore'

const Settings: React.FC = () => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const { logout, fetchCurrentUser } = useAuthStore()
  const [form] = Form.useForm()
  const [passwordForm] = Form.useForm()

  useEffect(() => {
    fetchUserInfo()
  }, [])

  const fetchUserInfo = async () => {
    try {
      const data = await authService.getCurrentUser()
      setUser(data)
      form.setFieldsValue({
        username: data.username,
        email: data.email,
        full_name: data.full_name,
      })
    } catch (error) {
      console.error('Failed to fetch user info:', error)
      message.error('获取用户信息失败')
    }
  }

  const handleProfileUpdate = async (values: any) => {
    setLoading(true)
    try {
      await userService.updateCurrentUser({
        email: values.email,
        full_name: values.full_name,
      })
      message.success('个人信息更新成功')
      await fetchCurrentUser() // Refresh context
      await fetchUserInfo()
    } catch (error) {
      console.error('Failed to update profile:', error)
      message.error('更新失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordUpdate = async (values: any) => {
    setLoading(true)
    try {
      await authService.changePassword(values.old_password, values.new_password)
      message.success('密码修改成功')
      passwordForm.resetFields()
    } catch (error) {
      console.error('Failed to change password:', error)
      message.error('密码修改失败，请检查旧密码是否正确')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteAccount = async () => {
    try {
      await userService.deleteCurrentUser()
      message.success('账号已删除')
      logout()
    } catch (error) {
      console.error('Failed to delete account:', error)
      message.error('删除账号失败')
    }
  }

  const items = [
    {
      key: '1',
      label: '个人资料',
      children: (
        <Card title="基本信息" bordered={false}>
          <Form
            form={form}
            layout="vertical"
            onFinish={handleProfileUpdate}
            initialValues={{ username: user?.username }}
          >
            <Form.Item label="用户名" name="username">
              <Input prefix={<UserOutlined />} disabled />
            </Form.Item>
            
            <Form.Item
              label="邮箱"
              name="email"
              rules={[
                { required: true, message: '请输入邮箱' },
                { type: 'email', message: '请输入有效的邮箱地址' },
              ]}
            >
              <Input />
            </Form.Item>

            <Form.Item label="全名" name="full_name">
              <Input />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={loading}>
                保存更改
              </Button>
            </Form.Item>
          </Form>
        </Card>
      ),
    },
    {
      key: '2',
      label: '安全设置',
      children: (
        <Card title="修改密码" bordered={false}>
          <Form form={passwordForm} layout="vertical" onFinish={handlePasswordUpdate}>
            <Form.Item
              label="当前密码"
              name="old_password"
              rules={[{ required: true, message: '请输入当前密码' }]}
            >
              <Input.Password prefix={<LockOutlined />} />
            </Form.Item>

            <Form.Item
              label="新密码"
              name="new_password"
              rules={[
                { required: true, message: '请输入新密码' },
                { min: 6, message: '密码长度至少6位' },
              ]}
            >
              <Input.Password prefix={<LockOutlined />} />
            </Form.Item>

            <Form.Item
              label="确认新密码"
              name="confirm_password"
              dependencies={['new_password']}
              rules={[
                { required: true, message: '请确认新密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('new_password') === value) {
                      return Promise.resolve()
                    }
                    return Promise.reject(new Error('两次输入的密码不一致'))
                  },
                }),
              ]}
            >
              <Input.Password prefix={<LockOutlined />} />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={loading}>
                修改密码
              </Button>
            </Form.Item>
          </Form>

          <div style={{ marginTop: 40, borderTop: '1px solid #f0f0f0', paddingTop: 20 }}>
            <h4 style={{ color: '#ff4d4f' }}>危险区域</h4>
            <Alert
              message="删除账号"
              description="删除账号后，您的所有数据（对话、API Key、模板等）都将被永久删除，无法恢复。"
              type="error"
              showIcon
              action={
                <Popconfirm
                  title="确定要删除账号吗？"
                  description="此操作不可逆，请谨慎操作。"
                  onConfirm={handleDeleteAccount}
                  okText="确定删除"
                  cancelText="取消"
                  okButtonProps={{ danger: true }}
                >
                  <Button danger icon={<DeleteOutlined />}>
                    删除账号
                  </Button>
                </Popconfirm>
              }
            />
          </div>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">设置</h1>
      <Tabs defaultActiveKey="1" items={items} />
    </div>
  )
}

export default Settings
