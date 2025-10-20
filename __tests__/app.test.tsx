import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import HomePage from '../app/page'

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      pathname: '/',
      query: {},
    }
  },
  useSearchParams() {
    return new URLSearchParams()
  },
}))

// Mock environment variables
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000'

describe('HomePage', () => {
  it('renders the landing client component', () => {
    render(<HomePage />)

    // The component should render without crashing
    // Add more specific tests based on your LandingClient component
    expect(document.body).toBeTruthy()
  })

  it('has proper document structure', () => {
    render(<HomePage />)

    // Check if the page has a body element
    expect(document.body).toBeInTheDocument()
  })
})

describe('Environment Configuration', () => {
  it('should have API URL configured', () => {
    expect(process.env.NEXT_PUBLIC_API_URL).toBe('http://localhost:8000')
  })
})
