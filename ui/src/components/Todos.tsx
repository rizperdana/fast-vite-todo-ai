import { Container, Stack } from "@chakra-ui/react";
import { createContext, useEffect, useState } from "react";


interface Todo {
    id: string;
    item: string;
}

const TodosContext = createContext({
    todos: [], fetchTodos: () => {}
})

export default function Todos() {
    const [todos, setTodos] = useState([])
    const fetchTodos = async () => {
        const response = await fetch("http://localhost:7777/todo")
        const todos = await response.json()
        setTodos(todos.data)
    }
    useEffect(() => {
        fetchTodos()
    }, [])

    return (
        <TodosContext.Provider value={{todos, fetchTodos}}>
            <Container maxW="container.x1" pt="100px">
                <Stack gap={5}>
                    {todos.map((todo: Todo) => (
                        <b key={todo.id}>{todo.item}</b>
                    ))}
                </Stack>
            </Container>
        </TodosContext.Provider>
    )
}
